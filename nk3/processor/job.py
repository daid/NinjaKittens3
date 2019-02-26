import logging

from typing import List

from nk3.machine.operation.jobOperationInstance import JobOperationInstance
from nk3.processor import pathUtils
from nk3.processor.settings import Settings

log = logging.getLogger(__name__.split(".")[-1])


class Job:
    def __init__(self, operation: JobOperationInstance):
        self.__settings = Settings()
        operation.fillProcessorSettings(self.__settings)
        self.__open_paths = pathUtils.Paths()
        self.__closed_paths = pathUtils.Paths()

    def addOpen(self, points: List[complex]) -> None:
        self.__open_paths.addPath(points, False)

    def addClosed(self, points: List[complex]) -> None:
        self.__closed_paths.addPath(points, True)

    @property
    def settings(self) -> Settings:
        return self.__settings

    @property
    def closedPaths(self):
        return self.__closed_paths

    @property
    def openPaths(self):
        return self.__open_paths
