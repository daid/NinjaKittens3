import inspect
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from typing import List, Generic, TypeVar, Any, Type, Dict, TYPE_CHECKING, Union, Callable

T = TypeVar("T")


class QProperty(Generic[T]):
    def __init__(self, default_value: T) -> None:
        self.default_value = default_value

    def __set__(self, instance: Any, value: T) -> None:
        pass

    def __get__(self, instance: Any, owner: Any) -> T:
        raise NotImplementedError()

    def getDefinedType(self) -> type:
        if TYPE_CHECKING:
            # mypy is not aware of the __orig_class__ that the Generic assigns.
            # So make it happy with a fake return. This type does not propegate anyhow,
            # as it's used for the pyqt property trickery.
            return object
        else:
            result = self.__orig_class__.__args__[0]
            if hasattr(result, "__origin__"): # In case of Generics, we need to grab the origin class, instead of the proxy.
                result = result.__origin__
            return result


if TYPE_CHECKING:  # mypy does not like the construct we use to get the metaclass of QObject. So fake a different metaclass.
    QObjectMetaClass = type
else:
    QObjectMetaClass = type(QObject)


class QObjectBaseMeta(QObjectMetaClass):
    def __new__(mcs, name: str, bases: Any, dct: Any) -> Any:
        new_dct = {}  # type: Dict[str, Any]
        for k, v in dct.items():
            if isinstance(v, QProperty):
                mcs.createProperty(new_dct, k, v.getDefinedType(), v.default_value)
        dct.update(new_dct)
        return super().__new__(mcs, name, bases, dct)

    @staticmethod
    def createProperty(dct: Dict[str, Any], name: str, property_type: Type[Any], default_value: Any) -> None:
        if issubclass(property_type, QObject):
            property_type = QObject

        value_key = "__%s" % (name)
        signal = pyqtSignal()
        signal_name = "%sChanged" % (name)
        @pyqtProperty(property_type, notify=signal)
        def getter(self: Any) -> Any:
            return getattr(self, value_key)
        @getter.setter
        def setter(self: Any, value: Any) -> None:
            setattr(self, value_key, value)
            getattr(self, signal_name).emit()

        dct[value_key] = default_value
        dct[name] = setter
        dct[signal_name] = signal
    
    # Workaround for python < 3.7, which lacks the __class_getitem__
    # And will call the __getitem__ of the metaclass for generics
    # So this is called for the QObjectList class when it is used as Generic
    def __getitem__(self, key: Any) -> Any:
        return self


class QObjectBase(QObject, metaclass=QObjectBaseMeta):
    pass


def _toQtType(t: type) -> Union[type, str]:
    if t == List[str]:
        return "QStringList"
    return t


## Type annotation aware version of pyqtSlot
def qtSlot(f: Callable[..., Any]) -> Callable[..., Any]:
    sig = inspect.signature(f)
    result_type = sig.return_annotation
    assert result_type != sig.empty, "Return annotation missing"
    parameters = []
    for par in sig.parameters.values():
        if par.name == "self":
            continue
        assert par.annotation != sig.empty, "Parameter annotation missing for %s" % (par.name)
        parameters.append(_toQtType(par.annotation))
    if result_type is not None:
        return pyqtSlot(*parameters, result=_toQtType(result_type))(f)
    return pyqtSlot(*parameters)(f)
