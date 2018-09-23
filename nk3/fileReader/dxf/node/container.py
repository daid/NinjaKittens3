import logging
from typing import Optional, Iterator
from .node import DxfNode
from . import nodeInfo

log = logging.getLogger(__name__.split(".")[-1])


class DxfContainerNode(DxfNode):
    def __init__(self, parent, name, end_of_container_node_name):
        super().__init__(parent, name)
        self.__children = []
        self.__end_of_container_node_name = end_of_container_node_name

    def processNewEntity(self, name: str) -> DxfNode:
        if name == self.__end_of_container_node_name:
            result = DxfNode(self.parent, name)
            return result
        if name in nodeInfo.containers:
            result = DxfContainerNode(self, name, nodeInfo.containers[name])
        else:
            result = DxfNode(self, name)
        self.__children.append(result)
        return result

    def find(self, type_name: str, name: str) -> Optional[DxfNode]:
        for child in self.__children:
            if child.type_name == type_name and child.name == name:
                return child
        return None

    def __iter__(self) -> Iterator[DxfNode]:
        return iter(self.__children)

    def dump(self, indent=0):
        super().dump(indent)
        for child in self.__children:
            child.dump(indent + 1)
