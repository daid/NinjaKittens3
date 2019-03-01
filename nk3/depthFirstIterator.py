import logging
from typing import Any, Optional, Callable, Iterator, List

log = logging.getLogger(__name__.split(".")[-1])


class DepthFirstIterator:
    def __init__(self, target: Any, *, include_root: bool=True, iter_function: Optional[Callable[[Any], Iterator[Any]]]=None) -> None:
        self.__list = []  # type: List[Any]
        self.__iter_function = iter_function if iter_function is not None else lambda n: n
        if include_root:
            self.__populate(target)
        else:
            for child in self.__iter_function(target):
                self.__populate(child)

    def __populate(self, node: Any) -> None:
        for child in self.__iter_function(node):
            self.__populate(child)
        self.__list.append(node)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__list)
