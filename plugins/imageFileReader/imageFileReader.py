import os
from typing import Iterable

from nk3.document.node import DocumentNode
from nk3.document.imageNode import DocumentImageNode
from nk3.fileReader.fileReader import FileReader


class ImageFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterable[str]:
        return "png", "jpg", "jpeg", "bmp"

    def __init__(self) -> None:
        super().__init__()

    def load(self, filename: str) -> DocumentNode:
        return DocumentImageNode(os.path.basename(filename), filename)
