from typing import Type, Dict, Iterable

from nk3.document.node import DocumentNode
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
