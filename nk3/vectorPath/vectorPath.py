from typing import List, Iterator


class VectorPath:
    def __init__(self) -> None:
        self.__points = []  # type: List[complex]
        self.__closed = False

    def add(self, point: complex) -> None:
        self.__points.append(point)

    def join(self, other: "VectorPath") -> None:
        if abs(self.end - other.start) < 0.001:
            self.__points += other.__points[1:]
        else:
            self.__points += other.__points
        other.__points = []
        other.__closed = False

    def offset(self, amount: complex) -> None:
        self.__points = [p + amount for p in self.__points]

    @property
    def empty(self) -> bool:
        return not self.__points

    @property
    def start(self) -> complex:
        return self.__points[0]

    @property
    def end(self) -> complex:
        return self.__points[-1]

    @property
    def closed(self) -> bool:
        return self.__closed

    def reverse(self) -> None:
        self.__points = self.__points[::-1]

    def close(self) -> None:
        self.__closed = True

    def __iter__(self) -> Iterator[complex]:
        return iter(self.__points)

    def getPoints(self) -> List[complex]:
        return self.__points.copy()
