from nk3.qt.QObjectList import QObjectList
from nk3.qt.QObjectBase import QProperty
from typing import Optional, Tuple


class DocumentNode(QObjectList["DocumentNode"]):
    name = QProperty[str]("")
    tool_index = QProperty[int](-1)
    operation_index = QProperty[int](-1)
    color = QProperty[int](0)

    def __init__(self, name: str) -> None:
        super().__init__("node")
        self.name = name

    def _getAABB(self) -> Optional[Tuple[complex, complex]]:
        return None

    def getAABB(self) -> Optional[Tuple[complex, complex]]:
        aabb = self._getAABB()
        for node in self:
            aabb_node = node.getAABB()
            if aabb and aabb_node:
                aabb = (
                    complex(min(aabb[0].real, aabb_node[0].real), min(aabb[0].imag, aabb_node[0].imag)),
                    complex(max(aabb[1].real, aabb_node[1].real), max(aabb[1].imag, aabb_node[1].imag))
                )
            elif aabb_node:
                aabb = aabb_node
        return aabb

    def getCenter(self) -> Optional[complex]:
        aabb = self.getAABB()
        if aabb is None:
            return None
        return (aabb[0] + aabb[1]) / 2.0

    def getSize(self) -> Optional[complex]:
        aabb = self.getAABB()
        if aabb is None:
            return None
        return aabb[1] - aabb[0]
