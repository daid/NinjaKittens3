import logging

from nk3.jobOperationInstance import JobOperationInstance
from nk3.processor.settings import Settings

log = logging.getLogger(__name__.split(".")[-1])

from typing import Dict

from nk3.cutToolType import CutToolType
from nk3.QObjectList import QObjectList
from nk3.QObjectBase import QObjectBaseProperty
from nk3.settingInstance import SettingInstance


class CutToolInstance(QObjectList):
    name = QObjectBaseProperty(str, "")
    operations = QObjectBaseProperty(QObjectList, None)

    def __init__(self, name: str, cut_tool_type: CutToolType):
        super().__init__()
        self.name = name
        self.operations = QObjectList()
        self.__type = cut_tool_type
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]

        for setting_type in cut_tool_type.getSettingTypes():
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

        for operation_type in cut_tool_type.getOperationTypes():
            self.operations.append(JobOperationInstance(self, operation_type))

    def fillProcessorSettings(self, settings: Settings) -> None:
        self.__type.fillProcessorSettings(self, settings)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
