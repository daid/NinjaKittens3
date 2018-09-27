from abc import ABC, abstractmethod

from typing import List, Iterator

from nk3.processor.settings import Settings
from nk3.settingType import SettingType


class JobOperationType(ABC):
    def __init__(self, default_name: str, settings: List[SettingType]):
        self.__default_name = default_name
        self.__settings = settings

    @property
    def defaultName(self):
        return self.__default_name

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    @abstractmethod
    def fillProcessorSettings(self, instance: "JobOperationInstance", settings: Settings) -> None:
        raise NotImplementedError
