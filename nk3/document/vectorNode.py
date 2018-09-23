import logging
import math
from typing import Optional, Tuple

from nk3.vectorPath.vectorPaths import VectorPaths
from .node import DocumentNode

log = logging.getLogger(__name__.split(".")[-1])


class DocumentVectorNode(DocumentNode):
    def __init__(self, name):
        super().__init__(name)
        self.__vector_paths = VectorPaths()

    def getPaths(self):
        return self.__vector_paths

    def getAABB(self) -> Optional[Tuple[complex, complex]]:
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = -float("inf"), -float("inf")
        for path in self.__vector_paths:
            for point in path:
                min_x = min(min_x, point.real)
                min_y = min(min_y, point.imag)
                max_x = max(max_x, point.real)
                max_y = max(max_y, point.imag)
        if math.isinf(min_x):
            return None
        return complex(min_x, min_y), complex(max_x, max_y)
