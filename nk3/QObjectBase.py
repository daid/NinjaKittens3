from collections import namedtuple
import inspect
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtWrapperType, pyqtSlot

QObjectBaseProperty = namedtuple("QObjectBaseProperty", ["type", "value"])


class QObjectBaseMeta(pyqtWrapperType):
    def __new__(mcs, name, bases, dct):
        new_dct = {}
        for k, v in dct.items():
            if isinstance(v, QObjectBaseProperty):
                mcs.createProperty(new_dct, k, v)
        dct.update(new_dct)
        return super().__new__(mcs, name, bases, dct)

    @staticmethod
    def createProperty(dct, name, property_data):
        value_key = "__%s" % (name)

        signal = pyqtSignal()
        signal_name = "%sChanged" % (name)
        @pyqtProperty(property_data.type, notify=signal)
        def f(self):
            return getattr(self, value_key)
        @f.setter
        def f(self, value):
            setattr(self, value_key, value)
            getattr(self, signal_name).emit()

        dct[value_key] = property_data.value
        dct[name] = f
        dct[signal_name] = signal


class QObjectBase(QObject, metaclass=QObjectBaseMeta):
    pass


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
        parameters.append(par.annotation)
    return pyqtSlot(*parameters, result=result_type)(f)
