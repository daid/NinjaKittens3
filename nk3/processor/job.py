from typing import List

from PyQt5.QtGui import QImage

from nk3.machine.machine import Machine
from nk3.machine.operation import Operation
from nk3.machine.tool import Tool
from nk3.processor import pathUtils
from nk3.processor.processorSettings import ProcessorSettings


class Job:
    def __init__(self, machine: Machine, tool: Tool, operation: Operation) -> None:
        self.__settings = ProcessorSettings()
        machine.fillProcessorSettings(self.__settings)
        tool.fillProcessorSettings(self.__settings)
        operation.fillProcessorSettings(self.__settings)
        self.__open_paths = pathUtils.Paths()
        self.__closed_paths = pathUtils.Paths()
        self.__images: List[QImage] = []

    def addOpen(self, points: List[complex]) -> None:
        self.__open_paths.addPath(points, False)

    def addClosed(self, points: List[complex]) -> None:
        self.__closed_paths.addPath(points, True)

    def addImage(self, image: QImage) -> None:
        self.__images.append(image)

    @property
    def settings(self) -> ProcessorSettings:
        return self.__settings

    @property
    def closedPaths(self) -> pathUtils.Paths:
        return self.__closed_paths

    @property
    def openPaths(self) -> pathUtils.Paths:
        return self.__open_paths

    @property
    def images(self) -> List[QImage]:
        return self.__images

