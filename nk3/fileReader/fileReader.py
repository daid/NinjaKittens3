from abc import ABC, abstractmethod

from typing import Iterator, Type, Dict

from nk3.document.node import DocumentNode
import importlib
import glob
import os


class FileReader(ABC):
    __EXTENSION_MAPPING = None

    def __init__(self):
        pass

    @abstractmethod
    def load(self, filename: str) -> DocumentNode:
        pass

    @staticmethod
    @abstractmethod
    def getExtensions() -> Iterator[str]:
        pass

    @staticmethod
    def getFileTypes() -> Dict[str, Type["FileReader"]]:
        if FileReader.__EXTENSION_MAPPING is None:
            mapping = {}
            base_path = os.path.dirname(__file__)
            for filename in glob.glob("%s/*/*.py" % (base_path)):
                filename = os.path.splitext(os.path.relpath(filename, base_path))[0]
                module_name = "nk3.fileReader.%s" % (filename.replace("\\", "/").replace("/", "."))
                module = importlib.import_module(module_name)
                for attrname in dir(module):
                    attr = getattr(module, attrname)
                    if type(attr) is type(FileReader) and issubclass(attr, FileReader) and attr != FileReader:
                        for extension in attr.getExtensions():
                            mapping[extension] = attr
            FileReader.__EXTENSION_MAPPING = mapping
        return FileReader.__EXTENSION_MAPPING
