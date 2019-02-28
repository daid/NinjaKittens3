import logging

from typing import Iterator, List, TYPE_CHECKING

from nk3.qt.QObjectBase import QObjectBase
from nk3.qt.QObjectList import QObjectList
from nk3.machine.tool.toolType import ToolType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
if TYPE_CHECKING:
    from nk3.machine.machineInstance import MachineInstance

log = logging.getLogger(__name__.split(".")[-1])


## The MachineType defines which type of tools are available for a machine, and some basic settings.
class MachineType(QObjectBase):
    def __init__(self, settings: List[SettingType], tools: List[ToolType]) -> None:
        super().__init__()
        self.__settings = settings
        self.__tools = QObjectList[ToolType]("tool_type")
        for tool in tools:
            self.__tools.append(tool)

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    def getToolTypes(self) -> QObjectList[ToolType]:
        return self.__tools

    def fillProcessorSettings(self, instance: "MachineInstance", settings: Settings) -> None:
        raise NotImplementedError
