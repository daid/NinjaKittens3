import logging
import os

from typing import Optional, List, Iterator

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.dxf.node.node import DxfNode
from nk3.fileReader.fileReader import FileReader
from nk3.vectorPath.vectorPaths import VectorPaths
from nk3.vectorPath.complexTransform import ComplexTransform
from nk3.vectorPath.nurbs import NURBS
from .dxfParser import DXFParser
from . import dxfConst
from .node.container import DxfContainerNode

log = logging.getLogger(__name__.split(".")[-1])


class DXFFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterator[str]:
        return "dxf",

    __IGNORED_ENTITIES = ("ATTDEF", "VIEWPORT", "XLINE", "POINT")

    def __init__(self):
        super().__init__()
        self.__block_by_name = {}
        self.__layer_by_name = {}

        self.__document_root = None  # type: DocumentNode
        self.__layers = {}  # type: List[DocumentNode]

    def load(self, filename: str) -> DocumentNode:
        parser = DXFParser(filename)
        self.__document_root = DocumentNode(os.path.basename(filename))

        # Phase 1, parse the DXF file into DxfContainerNodes and DxfNodes
        # These then contain the raw data from the DXF file, ready for next processing.
        root = DxfContainerNode(None, "ROOT", "EOF")
        parser.parse(root)
        # root.dump()

        # Phase 2, find layers and blocks, as we need those later on.
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

        # Phase 3, process each entity into path data.
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
        self._getPathFor(entity).addNurbs(nurbs)

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
