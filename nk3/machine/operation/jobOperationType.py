from abc import abstractmethod

from typing import List, Iterator, TYPE_CHECKING
from PyQt5.QtCore import QObject, pyqtProperty
from nk3.processor.settings import Settings
from nk3.settingType import SettingType

if TYPE_CHECKING:
    from nk3.machine.operation.jobOperationInstance import JobOperationInstance


class JobOperationType(QObject):
    def __init__(self, default_name: str, settings: List[SettingType]) -> None:
        super().__init__()
        self.__default_name = default_name
        self.__settings = settings

    @pyqtProperty(str, constant=True)
    def default_name(self) -> str:
        return self.__default_name

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    @abstractmethod
    def fillProcessorSettings(self, instance: "JobOperationInstance", settings: Settings) -> None:
        raise NotImplementedError
