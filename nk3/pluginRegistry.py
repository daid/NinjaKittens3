import importlib.util
import os
import sys
from typing import TypeVar, Optional, Type, Dict, cast

T = TypeVar("T")


class PluginRegistry:
    _instance = None

    @classmethod
    def getInstance(cls) -> "PluginRegistry":
        if cls._instance is None:
            cls._instance = PluginRegistry()
        return cls._instance

    def __init__(self) -> None:
        self.__classes = {}  # type: Dict[str, Type[object]]

    def findPlugins(self, path: str) -> None:
        sys.path.insert(0, path)
        for base_path, directories, files in os.walk(path):
            module_path = os.path.relpath(base_path, path).replace("/", ".")
            for file in files:
                if not file.endswith(".py"):
                    continue
                module_name = "%s.%s" % (module_path, file[:-3])
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr.__module__ == module_name:
                        self.register(attr)
        sys.path.pop(0)

    def register(self, register_class: Type[object]) -> None:
        assert register_class.__name__ not in self.__classes
        self.__classes[register_class.__name__] = register_class

    def getClass(self, base_class: Type[T], name: str) -> Optional[Type[T]]:
        if name in self.__classes:
            result = self.__classes[name]
            if issubclass(result, base_class):
                return cast(Type[T], result)
        return None
