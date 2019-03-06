import cmath
import logging
import math
import os
from typing import Optional, Iterable, Dict

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.fileReader import FileReader
from nk3.vectorPath.complexTransform import ComplexTransform
from nk3.vectorPath.nurbs import NURBS
from nk3.vectorPath.vectorPaths import VectorPaths
from . import _dxfConst
from ._dxfParser import DXFParser
from .node.container import DxfContainerNode
from .node.node import DxfNode

log = logging.getLogger(__name__.split(".")[-1])


class DXFFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterable[str]:
        return "dxf",

    __IGNORED_ENTITIES = ("ATTDEF", "VIEWPORT", "XLINE", "POINT")

    def __init__(self) -> None:
        super().__init__()
        self.__block_by_name = {}  # type: Dict[str, DxfContainerNode]
        self.__layer_by_name = {}  # type: Dict[str, DxfNode]

        self.__document_root = DocumentNode("PLACEHOLDER")
        self.__layers = {}  # type: Dict[str, DocumentNode]
        self.__transform_stack = [ComplexTransform()]

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
        if isinstance(blocks, DxfContainerNode):
            for block in blocks:
                assert isinstance(block, DxfContainerNode)
                self.__block_by_name[block.name] = block

        # Phase 3, process each entity into path data.
        entities = root.find("SECTION", "ENTITIES")
        if isinstance(entities, DxfContainerNode):
            for entity in entities:
                self._processEntity(entity)

        self._finish(self.__document_root)
        self._moveToOrigin(self.__document_root)
        return self.__document_root

    def _moveToOrigin(self, root_node: DocumentNode) -> None:
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

    def _finish(self, node: DocumentNode) -> None:
        if isinstance(node, DocumentVectorNode):
            node.getPaths().stitch()
        for child in node:
            self._finish(child)

    def _getPathFor(self, entity: DxfNode) -> VectorPaths:
        layer_name = str(entity.findEntry(8, default="NO_LAYER"))
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
        child.getPaths().setTransformStack(self.__transform_stack)
        return child.getPaths()

    def _getColorFor(self, entity: DxfNode) -> Optional[int]:
        color = entity.findEntry(420, default=None)
        if color is not None:
            return int(color)
        color = entity.findEntry(62, default=None)
        if color is not None:
            color_tuple = _dxfConst.colors[int(color)]
            return color_tuple[0] | color_tuple[1] << 8 | color_tuple[2] << 16
        return None

    def _processEntity(self, entity: DxfNode) -> None:
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
            log.warning("Unknown entity: %s", entity)
            # entity.dumpEntries()

    def _processLine(self, entity: DxfNode) -> None:
        start = entity.getComplex(10, 20)
        end = entity.getComplex(11, 21)
        self._getPathFor(entity).addLine(start, end)

    def _processCircle(self, entity: DxfNode) -> None:
        center = entity.getComplex(10, 20)
        radius = entity.getFloat(40)
        self._getPathFor(entity).addCircle(center, radius)

    def _processEllipse(self, entity: DxfNode) -> None:
        center = entity.getComplex(10, 20)
        major_axis_endpoint = entity.getComplex(11, 21)
        minor_major_ratio = entity.getFloat(40)
        start_angle = math.degrees(entity.getFloat(41))
        end_angle = math.degrees(entity.getFloat(42))
        # Note: Not sure if the start/end angle is handled properly, only seen full ellipses in example files.

        major_radius = abs(major_axis_endpoint)
        rotation = math.degrees(cmath.phase(major_axis_endpoint))
        self._getPathFor(entity).addArcByAngle(center, complex(major_radius, major_radius * minor_major_ratio), start_angle, end_angle, rotation=rotation)

    def _processPolyline(self, entity: DxfContainerNode) -> None:
        p0 = None
        bulge = 0.0
        path = self._getPathFor(entity)
        if entity.getInt(70) & 0x01:
            for vertex in entity:
                if vertex.type_name != "VERTEX":
                    log.warning("Ignoring unknown POLYLINE entry: %s", vertex)
                    continue
                p0 = vertex.getComplex(10, 20)
                bulge = vertex.getFloat(42)
        else:
            p0 = None
            bulge = 0.0
        for vertex in entity:
            if vertex.type_name != "VERTEX":
                log.warning("Ignoring unknown POLYLINE entry: %s", vertex)
                continue
            p1 = complex(vertex.getFloat(10), vertex.getFloat(20))
            if p0 is not None:
                if bulge == 0.0:
                    path.addLine(p0, p1)
                else:
                    path.addBulgeLine(p0, p1, bulge)
            bulge = vertex.getFloat(42)
            p0 = p1

    def _processLightWeightPolyline(self, entity: DxfNode) -> None:
        points = entity.getEntries(10, 20, 42)
        path = self._getPathFor(entity)
        if entity.getInt(70) & 0x01:
            p0 = complex(float(points[-1][0]), float(points[-1][1]))  # type: Optional[complex]
            bulge = float(points[-1][2])
        else:
            p0 = None
            bulge = 0.0
        for point in points:
            p1 = complex(float(point[0]), float(point[1]))
            if p0 is not None:
                if bulge is None or bulge == 0.0:
                    path.addLine(p0, p1)
                else:
                    path.addBulgeLine(p0, p1, bulge)
            p0 = p1
            bulge = float(point[2])

    def _processMLine(self, entity: DxfNode) -> None:
        path = self._getPathFor(entity)

        points = entity.getEntries(11, 21)
        p0 = entity.getComplex(10, 20)
        if entity.getInt(70) & 0x02:
            points.append([p0.real, p0.imag])
        for point in points:
            p1 = complex(float(point[0]), float(point[1]))
            path.addLine(p0, p1)
            p0 = p1
        log.warning("MLine processed, but not with offset lines")

    def _processSpline(self, entity: DxfNode) -> None:
        nurbs = NURBS(entity.getInt(71))
        for knot in entity.getEntries(40):
            nurbs.addKnot(float(knot[0]))
        for x, y in entity.getEntries(10, 20):
            nurbs.addPoint(complex(float(x), float(y)))
        self._getPathFor(entity).addNurbs(nurbs)

    def _processArc(self, entity: DxfNode) -> None:
        center = entity.getComplex(10, 20)
        radius = entity.getFloat(40)
        start_angle = entity.getFloat(50)
        end_angle = entity.getFloat(51)
        if end_angle < start_angle:
            end_angle += 360.0
        self._getPathFor(entity).addArcByAngle(center, complex(radius, radius), start_angle, end_angle)

    def _processInsert(self, entity: DxfNode) -> None:
        offset = entity.getComplex(10, 20)
        scale = complex(entity.getFloat(41, default=1.0), entity.getFloat(42, default=1.0))
        rotation = entity.getFloat(50)
        column_count = entity.getInt(70, default=1)
        row_count = entity.getInt(71, default=1)
        column_spacing = entity.getFloat(44, default=1.0)
        row_spacing = entity.getFloat(45, default=1.0)

        assert column_count == 1 and row_count == 1
        transform = ComplexTransform.rotate(rotation)\
            .combine(ComplexTransform.scale(scale))\
            .combine(ComplexTransform.translate(offset))
        self.__transform_stack.append(transform.combine(self.__transform_stack[-1]))
        for e in self.__block_by_name[entity.name]:
            self._processEntity(e)
        self.__transform_stack.pop()
