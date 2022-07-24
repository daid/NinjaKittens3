from typing import Type, Dict, Iterable

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.pluginRegistry import PluginRegistry


class FileReader:
    def __init__(self) -> None:
        pass

    def load(self, filename: str) -> DocumentNode:
        raise NotImplementedError

    @staticmethod
    def getExtensions() -> Iterable[str]:
        raise NotImplementedError

    @staticmethod
    def getFileTypes() -> Dict[str, Type["FileReader"]]:
        mapping = {}
        for class_ in PluginRegistry.getInstance().getAllClasses(FileReader):
            for extension in class_.getExtensions():
                mapping[extension] = class_
        return mapping

    @staticmethod
    def _moveToOrigin(root_node: DocumentNode) -> None:
        min_x = float("inf")
        min_y = float("inf")
        for node in DepthFirstIterator(root_node):
            aabb = node.getAABB()
            if aabb is not None:
                min_x = min(aabb[0].real, min_x)
                min_y = min(aabb[0].imag, min_y)
        for node in DepthFirstIterator(root_node):
            if isinstance(node, DocumentVectorNode):
                for path in node.getPaths():
                    path.offset(-complex(min_x, min_y))
