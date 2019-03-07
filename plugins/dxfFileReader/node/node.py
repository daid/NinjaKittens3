import logging
from typing import Optional, Union, List, Tuple

EntryTypes = Union[bool, int, float, str]


class DxfNode:
    def __init__(self, parent: Optional["DxfNode"], type_name: str) -> None:
        self.__parent = parent
        self.__type_name = type_name
        self.__name = str(id(self))
        self.__entries = []  # type: List[Tuple[int, EntryTypes]]

    def processNewEntity(self, name: str) -> "DxfNode":
        assert self.__parent is not None
        return self.__parent.processNewEntity(name)

    def processKey(self, group_code: int, value: EntryTypes) -> None:
        if group_code == 2:
            self.__name = str(value)
        self.__entries.append((group_code, value))

    @property
    def parent(self) -> Optional["DxfNode"]:
        return self.__parent

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type_name(self) -> str:
        return self.__type_name

    def getInt(self, key: int, *, default: int=0) -> int:
        for entry in self.__entries:
            if entry[0] == key:
                return int(entry[1])
        return default

    def getFloat(self, key: int, *, default: float=0.0) -> float:
        for entry in self.__entries:
            if entry[0] == key:
                return float(entry[1])
        return default

    def getComplex(self, key_real: int, key_imag: int) -> complex:
        return complex(self.getFloat(key_real), self.getFloat(key_imag))

    def findEntry(self, key: int, *, default: Optional[EntryTypes]=None) -> Optional[EntryTypes]:
        for entry in self.__entries:
            if entry[0] == key:
                return entry[1]
        return default

    def getEntries(self, *keys: int) -> List[List[EntryTypes]]:
        current = [0] * len(keys)  # type: List[EntryTypes]
        result = []  # type: List[List[EntryTypes]]
        for entry in self.__entries:
            if entry[0] in keys:
                index = keys.index(entry[0])
                if current[index] is not None:
                    result.append(current)
                    current = [0] * len(keys)
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

    def __repr__(self) -> str:
        return "%s:%s" % (self.__type_name, self.__name)

    def dump(self, indent: int=0) -> None:
        logging.info("%s%s", "  " * indent, self)

    def dumpEntries(self) -> None:
        logging.info("%s", self)
        for entry in self.__entries:
            logging.info("  %d: %s", entry[0], entry[1])
