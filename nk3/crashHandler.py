import sys
import traceback as traceback_module
import threading
from typing import Type, Optional
from types import TracebackType

from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtQml import QQmlApplicationEngine
from nk3.logging import LogHandler
from nk3.qt.QObjectBase import QObjectBase, qtSlot


class CrashHandler(QObjectBase):
    _original_excepthook = None
    _instance = None
    _main_thread = None

    @staticmethod
    def register() -> None:
        CrashHandler._original_excepthook = sys.excepthook
        CrashHandler._instance = CrashHandler()
        sys.excepthook = CrashHandler._instance.handleException
        _main_thread = threading.current_thread()

    def __init__(self) -> None:
        super().__init__()
        self.__crash_info = ""
        self.__qml_engine = None  # type: Optional[QQmlApplicationEngine]
        self.onShow.connect(self.show)

    def handleException(self, type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
        self.__crash_info = "--------Exception--------\n"
        self.__crash_info += "".join(traceback_module.format_exception(type_, value, traceback))
        self.__crash_info += "--------LOG--------\n"
        for message in LogHandler.getLogHistory():
            self.__crash_info += "%s\n" % (message)
        self.onShow.emit()
        if CrashHandler._original_excepthook is not None:
            CrashHandler._original_excepthook(type_, value, traceback)

    onShow = pyqtSignal()

    @qtSlot
    def show(self) -> None:
        self.__qml_engine = QQmlApplicationEngine()
        self.__qml_engine.rootContext().setContextProperty("crash_info", self.__crash_info)
        self.__qml_engine.load(QUrl("resources/qml/Crash.qml"))
