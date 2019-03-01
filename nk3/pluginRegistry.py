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

    def register(self, register_class: Type[object]) -> None:
        assert register_class.__name__ not in self.__classes
        self.__classes[register_class.__name__] = register_class

    def getClass(self, base_class: Type[T], name: str) -> Optional[Type[T]]:
        if name in self.__classes:
            result = self.__classes[name]
            if issubclass(result, base_class):
                return cast(Type[T], result)
        return None
