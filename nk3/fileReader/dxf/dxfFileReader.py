import logging
import os

from typing import Optional, List

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.dxf.node.node import DxfNode
from nk3.fileReader.fileReader import FileReader
from nk3.vectorPath.vectorPaths import VectorPaths
from nk3.vectorPath.complexTransform import ComplexTransform
from .dxfParser import DXFParser
from . import dxfConst
from .node.container import DxfContainerNode

log = logging.getLogger(__name__.split(".")[-1])


class DXFFileReader(FileReader):
    __IGNORED_ENTITIES = ("ATTDEF", "VIEWPORT", "XLINE", "POINT")

    def __init__(self):
        super().__init__()
        self.__block_by_name = {}
        self.__layer_by_name = {}

        self.__document_root = None  # type: DocumentNode
        self.__layers = {}  # type: List[DocumentNode]

    def load(self, filename: str):
        log.info("Going to load: %s", filename)
        parser = DXFParser(filename)
        self.__document_root = DocumentNode(os.path.basename(filename))

        # Phase 1, parse the DXF file into DxfContainerNodes and DxfNodes
        # These then contain the raw data from the DXF file, ready for next processing.
        root = DxfContainerNode(None, "ROOT", "EOF")
        parser.parse(root)
        # root.dump()

        tables = root.find("SECTION", "TABLES")
        if isinstance(tables, DxfContainerNode):
            layers_table = tables.find("TABLE", "LAYER")
            if isinstance(layers_table, DxfContainerNode):
                for layer in layers_table:
                    self.__layer_by_name[layer.name] = layer
        blocks = root.find("SECTION", "BLOCKS")
        if isinstance(tables, DxfContainerNode):
            for block in blocks:
                self.__block_by_name[block.name] = block

        entities = root.find("SECTION", "ENTITIES")
        if isinstance(entities, DxfContainerNode):
            for entity in entities:
                self._processEntity(entity)

        self._finish(self.__document_root)
        self._moveToOrigin(self.__document_root)
        return self.__document_root

    def _moveToOrigin(self, root_node):
        min_x = float("inf")
        min_y = float("inf")
        for node in DepthFirstIterator(root_node):
            aabb = node.getAABB()
            if aabb is not None:
                min_x = min(aabb[0].real, min_x)
                min_y = min(aabb[0].imag, min_y)
        for node in DepthFirstIterator(root_node):
            if isinstance(node, DocumentVectorNode):
                for path in node.getPaths():
                    path.offset(-complex(min_x, min_y))

    def _finish(self, node):
        if isinstance(node, DocumentVectorNode):
            node.getPaths().stitch()
        for child in node:
            self._finish(child)

    def _getPathFor(self, entity) -> VectorPaths:
        layer_name = entity.findEntry(8, default="NO_LAYER")
        color = self._getColorFor(entity)
        if color is None:
            if layer_name in self.__layer_by_name:
                color = self._getColorFor(self.__layer_by_name[layer_name])
        if layer_name not in self.__layers:
            self.__layers[layer_name] = DocumentNode("LAYER:%s" % (layer_name))
            self.__document_root.append(self.__layers[layer_name])
        node = self.__layers[layer_name]
        if color is not None:
            color_name = "#%02x%02x%02x" % (color & 0xFF, (color >> 8) & 0xFF, (color >> 16) & 0xFF)
        else:
            color_name = "NoColor"
        for child in node:
            if child.name == color_name:
                return child.getPaths()
        child = DocumentVectorNode(color_name)
        if color is not None:
            child.color = color
        node.append(child)
        return child.getPaths()

    def _getColorFor(self, entity: DxfNode) -> Optional[int]:
        color = entity.findEntry(420, default=None)
        if color is not None:
            return color
        color = entity.findEntry(62, default=None)
        if color is not None:
            color = dxfConst.colors[color]
            return color[0] | color[1] << 8 | color[2] << 16
        return None

    def _processEntity(self, entity):
        if entity.type_name == "LINE":
            self._processLine(entity)
        elif entity.type_name == "CIRCLE":
            self._processCircle(entity)
        elif entity.type_name == "ELLIPSE":
            self._processEllipse(entity)
        elif entity.type_name == "POLYLINE":
            assert isinstance(entity, DxfContainerNode)
            self._processPolyline(entity)
        elif entity.type_name == "LWPOLYLINE":
            self._processLightWeightPolyline(entity)
        elif entity.type_name == "MLINE":
            self._processMLine(entity)
        elif entity.type_name == "SPLINE":
            self._processSpline(entity)
        elif entity.type_name == "ARC":
            self._processArc(entity)
        elif entity.type_name == "INSERT":
            self._processInsert(entity)
        elif entity.type_name in self.__IGNORED_ENTITIES:
            pass
        else:
            log.info("Unknown entity: %s", entity)
            # entity.dumpEntries()

    def _processLine(self, entity):
        start = complex(entity[10], entity[20])
        end = complex(entity[11], entity[21])
        self._getPathFor(entity).addLine(start, end)

    def _processCircle(self, entity):
        center = complex(entity[10], entity[20])
        radius = entity[40]
        self._getPathFor(entity).addCircle(center, radius)

    def _processEllipse(self, entity):
        center = complex(entity[10], entity[20])
        major_axis_endpoint = complex(entity[11], entity[21])
        minor_major_ratio = entity[40]
        start_angle = entity[41]
        end_angle = entity[42]
        log.warning("Ignored ellipse")

    def _processPolyline(self, entity):
        p0 = None
        bulge = 0
        path = self._getPathFor(entity)
        if entity.findEntry(70, default=0) & 0x01:
            for vertex in entity:
                if vertex.type_name != "VERTEX":
                    log.warning("Ignoring unknown POLYLINE entry: %s", vertex)
                    continue
                p0 = complex(vertex[10], vertex[20])
                bulge = vertex.findEntry(42)
        else:
            p0 = None
            bulge = 0
        for vertex in entity:
            if vertex.type_name != "VERTEX":
                log.warning("Ignoring unknown POLYLINE entry: %s", vertex)
                continue
            p1 = complex(vertex[10], vertex[20])
            if p0 is not None:
                if bulge is None or bulge == 0.0:
                    path.addLine(p0, p1)
                else:
                    path.addBulgeLine(p0, p1, bulge)
            bulge = vertex.findEntry(42)
            p0 = p1

    def _processLightWeightPolyline(self, entity):
        points = entity.getEntries(10, 20, 42)
        path = self._getPathFor(entity)
        if entity.findEntry(70, default=0) & 0x01:
            p0 = complex(points[-1][0], points[-1][1])
            bulge = points[-1][2]
        else:
            p0 = None
            bulge = 0
        for point in points:
            p1 = complex(point[0], point[1])
            if p0 is not None:
                if bulge is None or bulge == 0.0:
                    path.addLine(p0, p1)
                else:
                    path.addBulgeLine(p0, p1, bulge)
            p0 = p1
            bulge = point[2]

    def _processMLine(self, entity):
        path = self._getPathFor(entity)

        points = entity.getEntries(11, 21)
        p0 = complex(entity[10], entity[20])
        if entity.findEntry(70, default=0) & 0x02:
            points.append((p0.real, p0.imag))
        for point in points:
            p1 = complex(point[0], point[1])
            path.addLine(p0, p1)
            p0 = p1
        log.warning("MLine processed, but not with offset lines")

    def _processSpline(self, entity):
        nurbs = NURBS(entity[71])
        for knot in entity.getEntries(40):
            nurbs.addKnot(knot[0])
        for x, y in entity.getEntries(10, 20):
            nurbs.addPoint(complex(x, y))
        points = nurbs.calculate(nurbs.pointCount())
        distance = 0
        for p0, p1 in zip(points[0:-1], points[1:]):
            distance += abs(p1 - p0)
        if distance < 1.0:
            point_count = int(max(2, distance / 0.1))
        elif distance < 5.0:
            point_count = int(max(2, distance / 0.3))
        else:
            point_count = int(max(2, distance / 0.5))
        path = self._getPathFor(entity)
        points = nurbs.calculate(point_count)
        for n in range(0, len(points) - 1):
            path.addLine(points[n], points[n + 1])

    def _processArc(self, entity):
        center = complex(entity[10], entity[20])
        radius = entity[40]
        start_angle = entity[50]
        end_angle = entity[51]
        if end_angle < start_angle:
            end_angle += 360.0
        self._getPathFor(entity).addArcByAngle(center, radius, start_angle, end_angle)

    def _processInsert(self, entity):
        offset = complex(entity[10], entity[20])
        scale = complex(entity.findEntry(41, default=1.0), entity.findEntry(42, default=1.0))
        rotation = entity.findEntry(50, default=0.0)
        column_count = entity.findEntry(70, default=1)
        row_count = entity.findEntry(71, default=1)
        column_spacing = entity.findEntry(44, default=1)
        row_spacing = entity.findEntry(45, default=1)

        log.info("%s", (offset, scale, rotation))
        assert column_count == 1 and row_count == 1
        transform = ComplexTransform.rotate(rotation)\
            .combine(ComplexTransform.scale(scale))\
            .combine(ComplexTransform.translate(offset))
        for e in self.__block_by_name[entity.name]:
            p = self._getPathFor(e)
            p.pushTransform(transform)
            self._processEntity(e)
            p.popTransform()


class NURBS:
    def __init__(self, degree: int) -> None:
        self._degree = degree
        self._points = []  # type: List[complex]
        self._weights = []  # type: List[float]
        self._knots = []  # type: List[float]

    def addPoint(self, p: complex) -> None:
        self._points.append(p)

    def addKnot(self, knot: float) -> None:
        self._knots.append(knot)

    def pointCount(self):
        return len(self._points)

    def calculate(self, segments: int) -> List[complex]:
        while len(self._weights) < len(self._points):
            self._weights.append(1.0)

        ret = []
        for n in range(0, segments):
            u = self._knots[0] + (self._knots[-1] - self._knots[0]) * n / (segments - 1)
            nku = []
            for m in range(0, len(self._points)):
                nku.append(self._weights[m] * self._N(m, self._degree, u))

            point = complex(0, 0)
            denom = sum(nku)
            for m in range(0, len(self._points)):
                if nku[m] != 0.0 and denom != 0.0:
                    r_iku = nku[m] / denom
                    if r_iku != 0.0:
                        point += self._points[m] * r_iku

            ret.append(point)
        return ret

    def _N(self, i: int, n: int, u: float) -> float:
        if n == 0:
            if self._knots[i] <= u <= self._knots[i+1]:
                return 1
            return 0
        else:
            Nin1u = self._N(i, n - 1, u)
            Ni1n1u = self._N(i + 1, n - 1, u)
            if Nin1u == 0.0:
                a = 0.0
            else:
                a = self._F(i, n, u) * Nin1u
            if Ni1n1u == 0.0:
                b = 0
            else:
                b = self._G(i, n, u) * Ni1n1u
            return a + b

    def _F(self, i: int, n: int, u: float) -> float:
        denom = self._knots[i + n] - self._knots[i]
        if denom == 0.0:
            return 0.0
        return (u - self._knots[i]) / denom

    def _G(self, i: int, n: int, u: float) -> float:
        denom = self._knots[i + n + 1] - self._knots[i]
        if denom == 0:
            return 0.0
        return (self._knots[i + n + 1] - u) / denom
