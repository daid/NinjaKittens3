from typing import NamedTuple, List

from nk3.processor.pathUtils import Path

Move = NamedTuple('Move', [('xy', complex), ('z', float), ('speed', float)])


class Result:
    def __init__(self):
        self.__moves = []  # type: List[Move]

    def addMove(self, move: Move) -> None:
        self.__moves.append(move)

    def addProblemRegion(self, path: Path) -> None:
        pass

    def addProblemPath(self, path: Path) -> None
        pass
