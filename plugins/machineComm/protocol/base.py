from typing import Optional
import abc


class ProtocolBase(abc.ABC):
    def __init__(self, status_callback) -> None:
        self.onStatusUpdate = status_callback

    @abc.abstractmethod
    def isConnected(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def sendRaw(self, raw_command: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def queueRaw(self, raw_command: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def abort(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def jog(self, *, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def zero(self, axis: str) -> None:
        raise NotImplementedError
