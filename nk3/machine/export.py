import logging
import os
import sys
from typing import List, Dict, Optional

import nk3.application
from nk3.processor.pathUtils import Move
from nk3.qt.QObjectBase import QProperty
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance
from nk3.settingType import SettingType

log = logging.getLogger(__name__.split(".")[-1])


class Export(QObjectList[SettingInstance]):
    save_button_text = QProperty[str]("?")
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
    def getMoves() -> List[Move]:
        return nk3.application.Application.getInstance().move_data

    # Set the qml source to a file inside the plugin that provides this Export type.
    def setLocalQmlSource(self, filename: str) -> None:
        path = os.path.dirname(sys.modules[type(self).__module__].__file__)
        self.qml_source = "file:///%s/%s" % (path, filename)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
