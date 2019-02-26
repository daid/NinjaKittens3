from nk3.QObjectList import QObjectList
from nk3.QObjectBase import QObjectBaseProperty
from typing import Optional, Tuple


class DocumentNode(QObjectList):
    name = QObjectBaseProperty[str]("")
    tool_index = QObjectBaseProperty[int](-1)
    operation_index = QObjectBaseProperty[int](-1)
    color = QObjectBaseProperty[int](0)

    def __init__(self, name):
        super().__init__("node")
        self.name = name

    def getAABB(self) -> Optional[Tuple[complex, complex]]:
        return None

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
