import logging
import pyclipper
from typing import List, NamedTuple, Tuple, Iterable, Set, Iterator

Move = NamedTuple('Move', [('xy', complex), ('z', float), ('speed', float)])


def dot(p0: complex, p1: complex) -> float:
    return p0.real * p1.real + p0.imag * p1.imag


class Path:
    def __init__(self, points: List[complex], closed: bool) -> None:
        self.__points = points
        self.__depth_at_distance = []  # type: List[Tuple[float, float]]
        self.__closed = closed
        self.__tags = set()  # type: Set[str]

    def addTag(self, tag: str) -> None:
        self.__tags.add(tag)

    def hasTag(self, tag: str) -> bool:
        return tag in self.__tags

    def shiftStartTowards(self, point: complex) -> None:
        if not self.__closed:
            return
        assert len(self.__depth_at_distance) == 0

        best_index = None
        for idx in range(len(self.__points)):
            if best_index is None or abs(point - self.__points[best_index]) > abs(point - self.__points[idx]):
                best_index = idx
        if best_index is not None:
            p0 = self.__points[best_index - 1]
            p1 = self.__points[best_index]
            p2 = self.__points[(best_index + 1) % len(self.__points)]
            dist0 = abs(p0 - p1)
            dist2 = abs(p2 - p1)
            norm0 = (p0 - p1) / dist0
            norm2 = (p2 - p1) / dist2
            dot0 = dot(point - p1, norm0)
            dot2 = dot(point - p1, norm2)
            dot0 = max(0.0, min(dot0, dist0))
            dot2 = max(0.0, min(dot2, dist2))
            q0 = p1 + norm0 * dot0
            q2 = p1 + norm2 * dot2
            if abs(q0 - point) > abs(q2 - point):
                q0 = q2
                best_index = (best_index + 1) % len(self.__points)
            if abs(q0 - self.__points[best_index]) == 0.0:
                self.__points = self.__points[best_index:] + self.__points[:best_index]
            else:
                self.__points = [q0] + self.__points[best_index:] + self.__points[:best_index]

    def removeDuplicates(self) -> None:
        idx = 0 if self.__closed else 1
        while idx < len(self.__points):
            if self.__points[idx - 1] == self.__points[idx]:
                self.__points.pop(idx)
            else:
                idx += 1

    def scoreCornering(self, start_offset: float, end_offset: float) -> float:
        p0 = self.__points[0]
        p1 = self.__points[0]
        offset = 0.0
        idx = 0
        corner_dot_values = []
        while offset < end_offset:
            p2 = self.__points[idx]
            idx = (idx + 1) % len(self.__points)
            offset += abs(p1 - p0)
            if start_offset < offset < end_offset and p0 != p1 and p1 != p2:
                norm0 = (p1 - p0) / abs(p1 - p0)
                norm2 = (p1 - p2) / abs(p1 - p2)
                corner_dot_values.append(1.0 + dot(norm0, norm2))
            p0 = p1
            p1 = p2
        return sum(corner_dot_values)

    def addDepthAtDistance(self, depth: float, distance: float) -> None:
        self.__depth_at_distance.append((distance, depth))
        self.__depth_at_distance.sort(key=lambda n: (n[0], -n[1]))

    def getTotalDepthDistance(self) -> float:
        return self.__depth_at_distance[-1][0]

    def getDepthAt(self, distance: float) -> float:
        for idx in range(len(self.__depth_at_distance) - 1):
            d0 = self.__depth_at_distance[idx]
            d1 = self.__depth_at_distance[idx + 1]
            if d0[0] <= distance < d1[0]:
                return d0[1] + (d1[1] - d0[1]) * (distance - d0[0]) / (d1[0] - d0[0])
        return self.__depth_at_distance[-1][1]

    def getMaxDepth(self) -> float:
        value = self.__depth_at_distance[0][1]
        for distance, depth in self.__depth_at_distance:
            value = min(value, depth)
        return value

    def iterateDepthPoints(self) -> Iterable[Tuple[complex, float]]:
        done_distance = 0.0
        points = self.__points
        if not self.__closed:
            points = points + list(reversed(points[1:-1]))
        p0 = points[0]
        point_index = 0
        depth_index = 0
        yield (p0, self.__depth_at_distance[depth_index][1])
        while depth_index + 1 < len(self.__depth_at_distance):
            p1 = points[(point_index + 1) % len(points)]
            next_move_distance = done_distance + abs(p1 - p0)

            next_depth_distance = self.__depth_at_distance[depth_index + 1][0]

            if next_move_distance < next_depth_distance:
                # Move to the next point in the path.
                point_index += 1
                done_distance = next_move_distance
                d0 = self.__depth_at_distance[depth_index]
                d1 = self.__depth_at_distance[depth_index + 1]
                yield (p1, d0[1] + (d1[1] - d0[1]) * (done_distance - d0[0]) / (d1[0] - d0[0]))
            else:
                # Move to a depth point in the path.
                if next_move_distance != done_distance:
                    p1 = p0 + (p1 - p0) * (next_depth_distance - done_distance) / (next_move_distance - done_distance)
                done_distance = next_depth_distance
                depth_index += 1
                yield (p1, self.__depth_at_distance[depth_index][1])
            p0 = p1

    def length(self) -> float:
        if len(self.__points) < 1:
            return 0.0
        result = 0.0
        if self.__closed:
            p0 = self.__points[-1]
        else:
            p0 = self.__points[0]
        for p1 in self.__points:
            result += abs(p0 - p1)
            p0 = p1
        return result

    def _toClipper(self) -> List[Tuple[float, float]]:
        return [(p.real * 1000.0, p.imag * 1000.0) for p in self.__points]

    @property
    def closed(self) -> bool:
        return self.__closed

    def __len__(self) -> int:
        return len(self.__points)

    def __getitem__(self, item: int) -> complex:
        return self.__points[item]


class Paths:
    def __init__(self) -> None:
        self.__paths = []  # type: List[Path]
        self.__children = []  # type: List[Paths]
        self.__is_hole = False

    def union(self) -> "Paths":
        clipper = pyclipper.Pyclipper()
        clipper.AddPaths(self._toClipper(), pyclipper.PT_SUBJECT, True)
        return Paths()._fromClipper(clipper.Execute(pyclipper.CT_UNION))

    def offset(self, amount: float, *, tree: bool=False) -> "Paths":
        offset = pyclipper.PyclipperOffset()
        offset.AddPaths(self._toClipper(), pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
        if tree:
            return Paths()._fromClipperTree(offset.Execute2(amount * 1000.0))
        else:
            return Paths()._fromClipper(offset.Execute(amount * 1000.0))

    def addPath(self, points: List[complex], closed: bool) -> None:
        self.__paths.append(Path(points, closed))

    def addChild(self, child: "Paths") -> None:
        self.__children.append(child)

    def combine(self, other: "Paths") -> None:
        self.__paths += other.__paths
        self.__children += other.__children

    def clear(self) -> None:
        self.__paths.clear()

    def _toClipper(self) -> List[List[Tuple[float, float]]]:
        return [path._toClipper() for path in self.__paths]

    def _fromClipper(self, paths: List[List[Tuple[float, float]]]) -> "Paths":
        self.__paths.clear()
        self.__children.clear()
        for path in paths:
            self.__paths.append(Path([complex(p[0] / 1000.0, p[1] / 1000) for p in path], True))
        return self

    def _fromClipperTree(self, node: pyclipper.PyPolyNode) -> "Paths":
        self.__paths.clear()
        self.__children.clear()
        self.__is_hole = node.IsHole
        self.__paths.append(Path([complex(p[0] / 1000.0, p[1] / 1000) for p in node.Contour], not node.IsOpen))
        for child in node.Childs:
            c = Paths()
            c._fromClipperTree(child)
            self.__children.append(c)
        return self

    @property
    def children(self) -> Iterator["Paths"]:
        return iter(self.__children)

    @property
    def isHole(self) -> bool:
        return self.__is_hole

    def __getitem__(self, item: int) -> Path:
        return self.__paths[item]

    def __iter__(self) -> Iterator[Path]:
        return iter(self.__paths)

    def __len__(self) -> int:
        return len(self.__paths)
