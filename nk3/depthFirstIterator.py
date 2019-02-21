import logging

log = logging.getLogger(__name__.split(".")[-1])


class DepthFirstIterator:
    def __init__(self, target, iter_function=None):
        self.__list = [target]
        self.__iter_function = iter_function if iter_function is not None else lambda n: n
        for child in self.__iter_function(target):
            self.__populate(child)

    def __populate(self, node):
        for child in self.__iter_function(node):
            self.__populate(child)
        self.__list.append(node)

    def __iter__(self):
        return iter(self.__list)
