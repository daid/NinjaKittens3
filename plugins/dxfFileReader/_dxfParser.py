import logging

from .node.container import DxfContainerNode
from .node.node import DxfNode
from ._dxfConst import group_type

log = logging.getLogger(__name__.split(".")[-1])


class DXFParser:
    def __init__(self, filename: str) -> None:
        # TODO: There is also a binary DXF format. Same concept with key-value pairs, but different format.
        #       However, I fail to find an real-life example of this.
        self.__file = open(filename, "rt")

    def parse(self, root_entity: DxfContainerNode) -> None:
        current_entity = root_entity  # type: DxfNode
        while True:
            group_code_str = self.__file.readline().strip()
            if group_code_str == "":
                self.__file.close()
                return
            group_code = int(group_code_str)
            value = self.__file.readline().strip()
            if group_code in group_type:
                try:
                    value = group_type[group_code](value)
                except ValueError:
                    log.warning("Failed to parse %s as %s (group code %d)", value, group_type[group_code], group_code)
            if group_code == 0:
                current_entity = current_entity.processNewEntity(value)
            else:
                current_entity.processKey(group_code, value)
