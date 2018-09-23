import logging

from typing import List, Tuple

from nk3.jobOperationInstance import JobOperationInstance
from nk3.processor.settings import Settings

log = logging.getLogger(__name__.split(".")[-1])


class Job:
    def __init__(self, operation: JobOperationInstance):
        self.__settings = Settings()
        operation.fillProcessorSettings(self.__settings)
        self.__open_paths = []
        self.__closed_paths = []

    def addOpen(self, points: List[Tuple[int, int]]) -> None:
        self.__open_paths.append(points)

    def addClosed(self, points: List[Tuple[int, int]]) -> None:
        self.__closed_paths.append(points)

    @property
    def settings(self) -> Settings:
        return self.__settings

    @property
    def closedPaths(self):
        return self.__closed_paths

    @property
    def openPaths(self):
        return self.__open_paths
