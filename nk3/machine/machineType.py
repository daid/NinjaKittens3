import logging

from typing import Iterator, List, TYPE_CHECKING, Type

from nk3.machine.tool import Tool
from nk3.qt.QObjectBase import QObjectBase
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType
if TYPE_CHECKING:
    from nk3.machine.machineInstance import MachineInstance

log = logging.getLogger(__name__.split(".")[-1])


## The MachineType defines which type of tools are available for a machine, and some basic settings.
class MachineType(QObjectBase):
    def __init__(self, settings: List[SettingType], tools: List[Type[Tool]]) -> None:
        super().__init__()
        self.__settings = settings
        self.__tool_types = tools

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    def getToolTypes(self) -> List[Type[Tool]]:
        return self.__tool_types

    def fillProcessorSettings(self, instance: "MachineInstance", settings: ProcessorSettings) -> None:
        raise NotImplementedError
