import logging

from typing import Iterator, List, TYPE_CHECKING

from nk3.QObjectBase import QObjectBase
from nk3.QObjectList import QObjectList
from nk3.jobOperationType import JobOperationType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
if TYPE_CHECKING:
    from nk3.cutToolInstance import CutToolInstance

log = logging.getLogger(__name__.split(".")[-1])


## The ToolType defines which settings and operations are available for specific tools
class ToolType(QObjectBase):
    def __init__(self, settings: List[SettingType], operations: List[JobOperationType]) -> None:
        super().__init__()
        self.__settings = settings
        self.__operations = QObjectList("operation")
        for operation in operations:
            self.__operations.append(operation)

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    def getOperationTypes(self) -> QObjectList:
        return self.__operations

    def fillProcessorSettings(self, instance: "CutToolInstance", settings: Settings) -> None:
        raise NotImplementedError
