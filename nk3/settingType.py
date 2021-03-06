from typing import Any

from PyQt5.QtCore import QObject, pyqtProperty


class SettingType(QObject):
    def __init__(self, *, key: str, label: str, type: str, default: str, tooltip: str) -> None:
        super().__init__()
        self.__key = key
        self.__label = label
        self.__type = type
        self.__default_value = default
        self.__tooltip = tooltip

    @pyqtProperty(str, constant=True)
    def key(self) -> str:
        return self.__key

    @pyqtProperty(str, constant=True)
    def label(self) -> str:
        return self.__label

    @pyqtProperty(str, constant=True)
    def type(self) -> str:
        return self.__type

    @pyqtProperty(str, constant=True)
    def default_value(self) -> str:
        return self.__default_value

    @pyqtProperty(str, constant=True)
    def tooltip(self) -> str:
        return self.__tooltip
