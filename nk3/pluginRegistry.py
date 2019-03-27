import importlib.util
import logging
import os
import sys
from typing import TypeVar, Optional, Type, Dict, cast, List

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
        for directory in os.listdir(path):
            if os.path.isdir(os.path.join(path, directory)):
                for file in os.listdir(os.path.join(path, directory)):
                    if not file.endswith(".py"):
                        continue
                    if file.startswith("_"):
                        continue
                    module_name = "%s.%s" % (directory, file[:-3])
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr.__module__ == module_name:
                            self.register(attr)
        sys.path.pop(0)

    def register(self, register_class: Type[object]) -> None:
        assert register_class.__name__ not in self.__classes
        if register_class.mro()[1] == object:
            return
        logging.info("Registering plugin: [%s] of type [%s]", register_class.__name__, register_class.mro()[1].__name__)
        self.__classes[register_class.__name__] = register_class

    def getClass(self, base_class: Type[T], class_name: str) -> Optional[Type[T]]:
        if class_name in self.__classes:
            result = self.__classes[class_name]
            if issubclass(result, base_class):
                return cast(Type[T], result)
        return None

    def createInstance(self, base_class: Type[T], class_name: str) -> Optional[T]:
        class_instance = self.getClass(base_class, class_name)
        if class_instance is None:
            logging.warning("Failed to find class: <%s> of type %s", class_name, base_class)
            return None
        return class_instance()

    def getAllClasses(self, base_class: Type[T]) -> List[Type[T]]:
        result = []
        for class_ in self.__classes.values():
            if issubclass(class_, base_class):
                result.append(cast(Type[T], class_))
        return result
