import logging
from typing import Optional, Union, List, Tuple

log = logging.getLogger(__name__.split(".")[-1])

EntryTypes = Union[bool, int, float, str]


class DxfNode:
    def __init__(self, parent, type_name):
        self.__parent = parent
        self.__type_name = type_name
        self.__name = str(id(self))
        self.__entries = []

    def processNewEntity(self, name: str) -> "DxfNode":
        return self.__parent.processNewEntity(name)

    def processKey(self, group_code: int, value: EntryTypes) -> None:
        if group_code == 2:
            self.__name = value
        self.__entries.append((group_code, value))

    @property
    def parent(self):
        return self.__parent

    @property
    def name(self):
        return self.__name

    @property
    def type_name(self):
        return self.__type_name

    def findEntry(self, key: int, *, default: Optional[EntryTypes]=None) -> Optional[EntryTypes]:
        for entry in self.__entries:
            if entry[0] == key:
                return entry[1]
        return default

    def getEntries(self, *keys: Tuple[int]) -> List[List[Optional[EntryTypes]]]:
        current = [None] * len(keys)
        result = []
        for entry in self.__entries:
            if entry[0] in keys:
                index = keys.index(entry[0])
                if current[index] is not None:
                    result.append(current)
                    current = [None] * len(keys)
                current[index] = entry[1]
        for n in current:
            if n is not None:
                result.append(current)
                break
        return result

    def __getitem__(self, key: int) -> EntryTypes:
        result = self.findEntry(key)
        if result is None:
            raise KeyError
        return result

    def __repr__(self):
        return "%s:%s" % (self.__type_name, self.__name)

    def dump(self, indent=0):
        log.info("%s%s", "  " * indent, self)

    def dumpEntries(self):
        log.info("%s", self)
        for entry in self.__entries:
            log.info("  %d: %s", entry[0], entry[1])
