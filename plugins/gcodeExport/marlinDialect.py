from typing import Optional

from nk3.processor.result import Move
from .gcodeDialect import GCodeDialect


class MarlinDialect(GCodeDialect):
    NAME = "Marlin"

    def __init__(self) -> None:
        self.__x = None  # type: Optional[float]
        self.__y = None  # type: Optional[float]
        self.__z = None  # type: Optional[float]
        self.__speed = None  # type: Optional[int]

    def convertMove(self, move: Move) -> str:
        result = "G1"
        if self.__speed != int(move.speed):
            self.__speed = int(move.speed)
            result += " F%d" % (self.__speed)
        if self.__x != move.xy.real:
            self.__x = move.xy.real
            result += " X%s" % self._toCompactNumber(self.__x)
        if self.__y != move.xy.imag:
            self.__y = move.xy.imag
            result += " Y%s" % self._toCompactNumber(self.__y)
        if self.__z != move.z:
            self.__z = move.z
            result += " Z%s" % self._toCompactNumber(self.__z)
        return result
