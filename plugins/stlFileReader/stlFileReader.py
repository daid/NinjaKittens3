import struct
from typing import Iterable, List, Tuple, Dict

from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.fileReader import FileReader


class STLFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterable[str]:
        return "stl",

    def __init__(self) -> None:
        super().__init__()
        self.__layers: Dict[str, DocumentVectorNode] = {}
        self.__root = DocumentVectorNode("Placeholder")

    def load(self, filename: str) -> DocumentNode:
        self.__root = DocumentVectorNode(filename)
        triangles = self._loadSTL(filename)
        for idx, (v0, v1, v2) in enumerate(triangles):
            print(idx, len(triangles))
            if v0[2] == v1[2] and v0[2] == v2[2]:
                continue
            if v0[2] == v1[2]:
                self._add(v0, v1, v2)
            elif v0[2] == v2[2]:
                self._add(v0, v2, v1)
            elif v1[2] == v2[2]:
                self._add(v1, v2, v0)

        for child in self.__root:
            child.getPaths().stitch()
        self.__root.setOrigin(0, 0)
        return self.__root

    def _add(self, v0: Tuple[float, float, float], v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> None:
        if v2[2] > v0[2]:
            return
        layer_name = f"{v0[2]:.0f} {v2[2]:.0f}"
        layer = self.__layers.get(layer_name)
        if layer is None:
            layer = DocumentVectorNode(layer_name)
            self.__layers[layer_name] = layer
            self.__root.append(layer)

        layer.getPaths().addLine(complex(v0[0], v0[1]), complex(v1[0], v1[1]))

    def _loadSTL(self, filename: str) -> List[Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]:
        f = open(filename, "rb")
        header = f.read(80)
        if header.upper().startswith(b'SOLID '):
            f.close()
            return self._loadSTLascii(filename)
        count = struct.unpack("<I", f.read(4))[0]
        result = []
        for n in range(count):
            triangle = struct.unpack("<ffffffffffffh", f.read(50))
            result.append(((triangle[3], triangle[4], triangle[5]), (triangle[6], triangle[7], triangle[8]), (triangle[9], triangle[10], triangle[11])))
        return result

    def _loadSTLascii(self, filename: str) -> List[Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]:
        raise NotImplementedError()
