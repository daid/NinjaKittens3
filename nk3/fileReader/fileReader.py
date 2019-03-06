import logging
from typing import Type, Dict, Iterable

from nk3.document.node import DocumentNode
from nk3.pluginRegistry import PluginRegistry

log = logging.getLogger(__name__.split(".")[-1])


class FileReader:
    __EXTENSION_MAPPING = None

    def __init__(self) -> None:
        pass

    def load(self, filename: str) -> DocumentNode:
        raise NotImplementedError

    @staticmethod
    def getExtensions() -> Iterable[str]:
        raise NotImplementedError

    @staticmethod
    def getFileTypes() -> Dict[str, Type["FileReader"]]:
        if FileReader.__EXTENSION_MAPPING is None:
            mapping = {}
            for class_ in PluginRegistry.getInstance().getAllClasses(FileReader):
                for extension in class_.getExtensions():
                    mapping[extension] = class_
            FileReader.__EXTENSION_MAPPING = mapping
        return FileReader.__EXTENSION_MAPPING
