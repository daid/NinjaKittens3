from abc import ABC, abstractmethod

from typing import List, Iterator

from PyQt5.QtCore import QObject, pyqtProperty

from nk3.processor.settings import Settings
from nk3.settingType import SettingType


class JobOperationType(QObject):
    def __init__(self, default_name: str, settings: List[SettingType]):
        super().__init__()
        self.__default_name = default_name
        self.__settings = settings

    @pyqtProperty(str, constant=True)
    def default_name(self):
        return self.__default_name

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    @abstractmethod
    def fillProcessorSettings(self, instance: "JobOperationInstance", settings: Settings) -> None:
        raise NotImplementedError
