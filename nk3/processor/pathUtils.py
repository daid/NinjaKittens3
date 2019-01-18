import logging
from typing import List, NamedTuple, Union, Tuple, Optional
import pyclipper

log = logging.getLogger(__name__.split(".")[-1])


Move = NamedTuple('Move', [('xy', Optional[complex]), ('z', float), ('speed', float)])
TreeNode = NamedTuple("TreeNode", [("contour", List[complex]), ("children", List["TreeNode"]), ("hole", bool)])


def _toClipper(paths: List[List[complex]]) -> List[List[Tuple[float, float]]]:
    return [[(p.real * 1000.0, p.imag * 1000.0) for p in path] for path in paths]


def _fromClipper(paths: List[List[Tuple[float, float]]]) -> List[List[complex]]:
    return [[complex(p[0] / 1000.0, p[1] / 1000) for p in path] for path in paths]


def _fromClipperTree(node: pyclipper.PyPolyNode) -> TreeNode:
    return TreeNode([complex(p[0] / 1000.0, p[1] / 1000) for p in node.Contour], [_fromClipperTree(n) for n in node.Childs], node.IsHole)


def length(path: List[complex]) -> float:
    result = 0.0
    p0 = path[-1]
    for p1 in path:
        result += abs(p0 - p1)
        p0 = p1
    return result


def union(paths: List[List[complex]]) -> List[List[complex]]:
    if len(paths) < 1:
        return []
    clipper = pyclipper.Pyclipper()
    clipper.AddPaths(_toClipper(paths), pyclipper.PT_SUBJECT, True)
    return _fromClipper(clipper.Execute(pyclipper.CT_UNION))


def offset(paths: List[List[complex]], amount: float, *, tree=False) -> Union[List[List[complex]], TreeNode]:
    offset = pyclipper.PyclipperOffset()
    offset.AddPaths(_toClipper(paths), pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
    if tree:
        return _fromClipperTree(offset.Execute2(amount * 1000.0))
    else:
        return _fromClipper(offset.Execute(amount * 1000.0))


def insertPoint(offset_distance: float, path: List[complex], depth: Optional[List[float]]=None):
    a = 0.0
    p0 = None
    while True:
        for n in range(0, len(path)):
            p1 = path[n]
            if p0 is not None:
                step = abs(p0 - p1)
                if a + step > offset_distance:
                    path.insert(n, p0 + (p1 - p0) / step * (offset_distance - a))
                    if depth is not None:
                        d0 = depth[n-1]
                        d1 = depth[n]
                        depth.insert(n, d0 + (d1 - d0) / step * (offset_distance - a))
                    return
                a += step
            p0 = p1
