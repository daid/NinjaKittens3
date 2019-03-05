import logging

from typing import Iterator, List, TYPE_CHECKING, Type

from nk3.machine.operation import Operation
from nk3.qt.QObjectBase import QObjectBase
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType
if TYPE_CHECKING:
    from nk3.machine.tool.toolInstance import ToolInstance

log = logging.getLogger(__name__.split(".")[-1])


## The ToolType defines which settings and operations are available for specific tools
class ToolType(QObjectBase):
    def __init__(self, settings: List[SettingType], operations: List[Type[Operation]]) -> None:
        super().__init__()
        self.__settings = settings
        self.__operations = operations

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    def getOperationTypes(self) -> List[Type[Operation]]:
        return self.__operations

    def fillProcessorSettings(self, instance: "ToolInstance", settings: ProcessorSettings) -> None:
        raise NotImplementedError
