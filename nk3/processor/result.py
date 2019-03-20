from typing import NamedTuple, List, Iterator, Optional

from nk3.processor.pathUtils import Paths

Move = NamedTuple('Move', [('xy', complex), ('z', float), ('speed', float)])


class Result:
    def __init__(self) -> None:
        self.__moves = []  # type: List[Move]
        self.__xy_speed = 0.0
        self.__xy_travel_speed = 0.0
        self.__z_down_speed = 0.0
        self.__z_up_speed = 0.0

        self.__problem_regions = Paths()

    def setSpeeds(self, *, xy_speed: float, xy_travel_speed: float, z_down_speed: float, z_up_speed: float) -> None:
        self.__xy_speed = xy_speed
        self.__xy_travel_speed = xy_travel_speed
        self.__z_down_speed = z_down_speed
        self.__z_up_speed = z_up_speed

    def addMove(self, xy: complex, z: float) -> None:
        self.__addMove(xy, z, self.__xy_speed)

    def addTravel(self, xy: complex, z: float) -> None:
        self.__addMove(xy, z, self.__xy_travel_speed)

    def __addMove(self, xy: complex, z: float, xy_speed: float) -> None:
        speed = xy_speed
        if len(self.__moves) > 0:
            xy_distance = abs(self.__moves[-1].xy - xy)
            z_distance = z - self.__moves[-1].z
            total_distance = abs(complex(xy_distance, z_distance))
            if total_distance == 0.0:
                return
            z_speed = self.__z_down_speed if z_distance < 0 else self.__z_up_speed
            # Make it so that:
            # speed * xy_distance / total_distance = xy_speed
            # speed * z_distance / total_distance = z_speed
            if xy_distance != 0.0 and z_distance != 0.0:
                speed = min(xy_speed / xy_distance * total_distance, z_speed / abs(z_distance) * total_distance)
            elif xy_distance != 0.0:
                speed = xy_speed / xy_distance * total_distance
            else:
                speed / abs(z_distance) * total_distance
        self.__moves.append(Move(xy, z, speed))

    def getLastXY(self) -> Optional[complex]:
        if not self.__moves:
            return None
        return self.__moves[-1].xy

    def addProblemRegions(self, paths: Paths) -> None:
        self.__problem_regions.combine(paths)

    def addProblemPath(self, path: Paths) -> None:
        pass

    @property
    def moves(self) -> Iterator[Move]:
        return iter(self.__moves)
