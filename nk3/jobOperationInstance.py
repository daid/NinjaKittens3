from typing import Dict

from nk3.jobOperationType import JobOperationType
from nk3.QObjectList import QObjectList
from nk3.QObjectBase import QObjectBaseProperty
from nk3.processor.settings import Settings
from nk3.settingInstance import SettingInstance


class JobOperationInstance(QObjectList):
    name = QObjectBaseProperty(str, "")

    def __init__(self, tool_instance: "CutToolInstance", job_operation_type: JobOperationType) -> None:
        super().__init__()
        self.name = job_operation_type.defaultName
        self.__tool = tool_instance
        self.__type = job_operation_type
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]
        for setting_type in job_operation_type.getSettingTypes():
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @property
    def type(self):
        return self.__type

    def fillProcessorSettings(self, settings: Settings):
        self.__tool.fillProcessorSettings(settings)
        self.__type.fillProcessorSettings(self, settings)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
