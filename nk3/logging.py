import logging
from typing import List, Any


def setup() -> None:
    handlers = []  # type: List[logging.Handler]
    HAS_CONSOLE = True  # TODO: How to detect if we have a attached console or not.
    if HAS_CONSOLE:
        handlers.append(logging.StreamHandler())
    handlers.append(LogHandler())
    logging.basicConfig(handlers=handlers, format="%(asctime)s:%(levelname)10s:%(module)20s:%(message)s", level=logging.INFO)


class LogHandler(logging.Handler):
    _instance = None

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.__history = []  # type: List[str]
        LogHandler._instance = self

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.__history.append(msg)
        if len(self.__history) > 32:
            self.__history.pop(0)

    @staticmethod
    def getLogHistory() -> List[str]:
        if LogHandler._instance is None:
            return []
        return LogHandler._instance.__history.copy()
