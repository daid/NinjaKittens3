import importlib
import logging
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import Type, Dict, TYPE_CHECKING, Iterable

from nk3.document.node import DocumentNode

log = logging.getLogger(__name__.split(".")[-1])

if TYPE_CHECKING:
    from .dxf.dxfFileReader import DXFFileReader
    from .svg.svgFileReader import SVGFileReader


class FileReader(ABC):
    __EXTENSION_MAPPING = None

    def __init__(self) -> None:
        pass

    @abstractmethod
    def load(self, filename: str) -> DocumentNode:
        pass

    @staticmethod
    @abstractmethod
    def getExtensions() -> Iterable[str]:
        pass

    @staticmethod
    def getFileTypes() -> Dict[str, Type["FileReader"]]:
        if FileReader.__EXTENSION_MAPPING is None:
            mapping = {}
            base_path = os.path.dirname(__file__)
            for _, base_module_name, ispkg in pkgutil.walk_packages([base_path]):
                if not ispkg:
                    continue
                for _, sub_module_name, ispkg in pkgutil.walk_packages([base_path + "/" + base_module_name]):
                    module_name = "nk3.fileReader.%s.%s" % (base_module_name, sub_module_name)
                    module = importlib.import_module(module_name)
                    for attrname in dir(module):
                        attr = getattr(module, attrname)
                        if type(attr) is type(FileReader) and issubclass(attr, FileReader) and attr != FileReader:
                            for extension in attr.getExtensions():
                                mapping[extension] = attr
            FileReader.__EXTENSION_MAPPING = mapping
        return FileReader.__EXTENSION_MAPPING
