import inspect
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from typing import List, Generic, TypeVar, Any, Type, Dict

T = TypeVar("T")


class QObjectBaseProperty(Generic[T]):
    def __init__(self, default_value):
        self.default_value = default_value

    def __set__(self, instance, value: T) -> None:
        pass

    def __get__(self, instance, owner) -> T:
        pass


class QObjectBaseMeta(type(QObject)):
    def __new__(mcs, name, bases, dct):
        new_dct = {}
        for k, v in dct.items():
            if isinstance(v, QObjectBaseProperty):
                mcs.createProperty(new_dct, k, v.__orig_class__.__args__[0], v.default_value)
        dct.update(new_dct)
        return super().__new__(mcs, name, bases, dct)

    @staticmethod
    def createProperty(dct: Dict[str, Any], name: str, property_type: Type[Any], default_value: Any) -> None:
        value_key = "__%s" % (name)

        signal = pyqtSignal()
        signal_name = "%sChanged" % (name)
        @pyqtProperty(property_type, notify=signal)
        def f(self):
            return getattr(self, value_key)
        @f.setter
        def f(self, value):
            setattr(self, value_key, value)
            getattr(self, signal_name).emit()

        dct[value_key] = default_value
        dct[name] = f
        dct[signal_name] = signal


class QObjectBase(QObject, metaclass=QObjectBaseMeta):
    pass


def _toQtType(t):
    if t == List[str]:
        return "QStringList"
    return t


## Type annotation aware version of pyqtSlot
def qtSlot(f):
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
