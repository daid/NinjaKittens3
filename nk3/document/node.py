from nk3.qt.QObjectList import QObjectList
from nk3.qt.QObjectBase import QProperty
from nk3.depthFirstIterator import DepthFirstIterator
from typing import Optional, Tuple
from PyQt5.QtCore import pyqtProperty, pyqtSignal


class DocumentNode(QObjectList["DocumentNode"]):
    name = QProperty[str]("")
    tool_index = QProperty[int](-1)
    operation_index = QProperty[int](-1)
    color = QProperty[int](0)

    color_signal = pyqtSignal()
    @pyqtProperty(str, notify=color_signal)
    def color_string(self):
        return f"#{self.color:06x}"

    def __init__(self, name: str) -> None:
        super().__init__("node")
        self.name = name

    def offset(self, offset: complex) -> None:
        pass

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

    def setOrigin(self, x: float, y: float) -> None:
        aabb = self.getAABB()
        if aabb is None:
            return
        offset_x = aabb[0].real + (aabb[1].real - aabb[0].real) * x
        offset_y = aabb[0].imag + (aabb[1].imag - aabb[0].imag) * y
        for node in DepthFirstIterator(self):
            node.offset(-complex(offset_x, offset_y))
