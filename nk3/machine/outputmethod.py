import os
import sys
from typing import List, Dict, Optional, Iterator

from PyQt5.QtCore import pyqtProperty

import nk3.application
from nk3.processor.result import Move
from nk3.qt.QObjectBase import QProperty
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance
from nk3.settingType import SettingType


class OutputMethod(QObjectList[SettingInstance]):
    NAME = "Unnamed Output Method"

    qml_source = QProperty[str]("")

    def __init__(self, settings: Optional[List[SettingType]] = None) -> None:
        super().__init__("setting")
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]

        if settings is not None:
            for setting_type in settings:
                instance = SettingInstance(setting_type)
                self.append(instance)
                self.__setting_instances[instance.type.key] = instance

    @staticmethod
    def getMoves() -> Iterator[Move]:
        return nk3.application.Application.getInstance().result_data.moves

    # Set the qml source to a file inside the plugin that provides this output method type.
    def setLocalQmlSource(self, filename: str) -> None:
        path = os.path.dirname(sys.modules[type(self).__module__].__file__)
        self.qml_source = "file:///%s/%s" % (path, filename)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value

    # Called when this output method is on the current active machine.
    # Override in subclass as needed.
    def activate(self) -> None:
        pass

    # Called when this output method is no longer on the active machine, or being removed.
    # Override in subclass as needed.
    def release(self) -> None:
        pass

    @pyqtProperty(str, constant=True)
    def typename(self) -> str:
        return self.NAME
