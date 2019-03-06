import sys
import traceback as traceback_module
from typing import Type
from types import TracebackType

from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QQmlApplicationEngine


class CrashHandler:
    _original_excepthook = None
    _instance = None

    @staticmethod
    def register() -> None:
        CrashHandler._original_excepthook = sys.excepthook
        sys.excepthook = CrashHandler.handleException

    @staticmethod
    def handleException(type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
        CrashHandler._instance = CrashHandler(type_, value, traceback)
        CrashHandler._instance.show()

    def __init__(self, type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
        self.__crash_info = "".join(traceback_module.format_exception(type_, value, traceback))
        self.__qml_engine = QQmlApplicationEngine()
        if CrashHandler._original_excepthook is not None:
            CrashHandler._original_excepthook(type_, value, traceback)

    def show(self) -> None:
        self.__qml_engine.rootContext().setContextProperty("crash_info", self.__crash_info)
        self.__qml_engine.load(QUrl("resources/qml/Crash.qml"))
