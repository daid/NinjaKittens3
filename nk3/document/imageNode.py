import numpy
from typing import Optional, Tuple
from PyQt5.QtGui import QImage, QOpenGLTexture
from .node import DocumentNode


class DocumentImageNode(DocumentNode):
    def __init__(self, name: str, filename: str) -> None:
        super().__init__(name)
        self.__offset = complex()

        self.qimage = QImage()
        self.qimage.load(filename)
        self.opengl_texture: Optional[QOpenGLTexture] = None

    def offset(self, offset: complex) -> None:
        self.__offset += offset

    def _transform(self, xx: float, xy: float, yx: float, yy: float) -> None:
        pass

    def _getAABB(self) -> Optional[Tuple[complex, complex]]:
        return complex(0, 0), complex(self.qimage.size().width(), self.qimage.size().height())
