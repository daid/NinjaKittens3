import logging

from typing import Iterator, List, TYPE_CHECKING

from nk3.QObjectBase import QObjectBase
from nk3.QObjectList import QObjectList
from nk3.machine.operation.jobOperationType import JobOperationType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
if TYPE_CHECKING:
    from nk3.machine.tool.toolInstance import ToolInstance

log = logging.getLogger(__name__.split(".")[-1])


## The ToolType defines which settings and operations are available for specific tools
class ToolType(QObjectBase):
    def __init__(self, settings: List[SettingType], operations: List[JobOperationType]) -> None:
        super().__init__()
        self.__settings = settings
        self.__operations = QObjectList("operation_type")
        for operation in operations:
            self.__operations.append(operation)

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    def getOperationTypes(self) -> QObjectList:
        return self.__operations

    def fillProcessorSettings(self, instance: "ToolInstance", settings: Settings) -> None:
        raise NotImplementedError
