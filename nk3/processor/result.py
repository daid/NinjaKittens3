from typing import NamedTuple

from nk3.processor.pathUtils import Path

Move = NamedTuple('Move', [('xy', complex), ('z', float), ('speed', float)])


class Result:
    def __init__(self):
        self.__moves = []

    def addMove(self, move: Move):
        self.__moves.append(move)

    def addProblemRegion(self, path: Path):
        pass

    def addProblemPath(self, path: Path):
        pass
