from typing import Dict, TYPE_CHECKING, List

from nk3.qt.QObjectList import QObjectList
from nk3.qt.QObjectBase import QProperty
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingInstance import SettingInstance
from nk3.settingType import SettingType

if TYPE_CHECKING:
    from nk3.machine.tool.toolInstance import ToolInstance


class Operation(QObjectList[SettingInstance]):
    DEFAULT_NAME = "Unknown"

    name = QProperty[str]("")

    def __init__(self, settings: List[SettingType]) -> None:
        super().__init__("setting")
        self.name = self.DEFAULT_NAME
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]
        for setting_type in settings:
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        raise NotImplementedError

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
