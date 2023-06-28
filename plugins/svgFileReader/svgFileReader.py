import logging
import math
import re
from typing import Iterable, Optional
from xml.etree import ElementTree

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.fileReader import FileReader
from nk3.vectorPath.complexTransform import ComplexTransform


class SVGFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterable[str]:
        return "svg",

    def __init__(self) -> None:
        super().__init__()
        self.__xml = None  # type: Optional[ElementTree.ElementTree]
        dpi = 90.0
        dpi = 25.4
        self.__transform_stack = [ComplexTransform.scale(complex(25.4/dpi, -25.4/dpi))]

    def load(self, filename: str) -> DocumentNode:
        self.__xml = ElementTree.parse(filename)
        root_node = DocumentVectorNode(filename)
        root_node.getPaths().setTransformStack(self.__transform_stack)
        self.__processGTag(self.__xml.getroot(), root_node)
        for node in DepthFirstIterator(root_node):
            node.getPaths().stitch()
        root_node.setOrigin(0, 0)
        return root_node

    def __processGTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        for child in tag:
            if child.get("transform"):
                self.__pushTransform(str(child.get("transform")))
            child_tag = child.tag[child.tag.find('}') + 1:].lower()
            if child_tag == "g" or child_tag == "a":
                self.__processGTag(child, node)
            elif child_tag == "line":
                self.__processLineTag(child, self.__getNodeFor(child, node))
            elif child_tag == "polyline":
                self.__processPolylineTag(child, self.__getNodeFor(child, node))
            elif child_tag == "polygon":
                self.__processPolygonTag(child, self.__getNodeFor(child, node))
            elif child_tag == "circle":
                self.__processCircleTag(child, self.__getNodeFor(child, node))
            elif child_tag == "ellipse":
                self.__processEllipseTag(child, self.__getNodeFor(child, node))
            elif child_tag == "path":
                self.__processPathTag(child, self.__getNodeFor(child, node))
            elif child_tag == "rect":
                self.__processRectTag(child, self.__getNodeFor(child, node))
            elif child_tag in ("desc", "title", "animate", "animateColor", "animateTransform", "script", "namedview", "metadata"):
                pass  # ignore these tags, as they contain no value for us.
            else:
                logging.warning("Unknown svg tag: %s", child_tag)
            if child.get("transform"):
                self.__transform_stack.pop()

    def __processLineTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        x1 = float(tag.attrib.get('x1', 0))
        y1 = float(tag.attrib.get('y1', 0))
        x2 = float(tag.attrib.get('x2', 0))
        y2 = float(tag.attrib.get('y2', 0))
        node.getPaths().addLine(complex(x1, y1), complex(x2, y2))

    def __processPolylineTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        paths = node.getPaths()
        values = list(map(float, re.split('[, \t]+', tag.attrib.get('points', '').strip())))
        p0 = complex(values[0], values[1])
        for n in range(2, len(values)-1, 2):
            p1 = complex(values[n], values[n + 1])
            paths.addLine(p0, p1)
            p0 = p1

    def __processPolygonTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        paths = node.getPaths()
        values = list(map(float, re.split('[, \t]+', tag.attrib.get('points', '').strip())))
        start = p0 = complex(values[0], values[1])
        for n in range(2, len(values)-1, 2):
            p1 = complex(values[n], values[n + 1])
            paths.addLine(p0, p1)
            p0 = p1
        paths.addLine(p0, start)

    def __processCircleTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        cx = float(tag.attrib.get('cx', '0'))
        cy = float(tag.attrib.get('cy', '0'))
        r = float(tag.attrib.get('r', '0'))
        paths = node.getPaths()
        paths.addCircle(complex(cx, cy), r)

    def __processEllipseTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        cx = float(tag.attrib.get('cx', '0'))
        cy = float(tag.attrib.get('cy', '0'))
        rx = float(tag.attrib.get('rx', '0'))
        ry = float(tag.attrib.get('ry', '0'))
        paths = node.getPaths()
        paths.addArcByAngle(complex(cx, cy), complex(rx, ry), 0, 360)

    def __processRectTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        paths = node.getPaths()
        x = float(tag.attrib.get("x", 0))
        y = float(tag.attrib.get("y", 0))
        w = float(tag.attrib.get("width", 0))
        h = float(tag.attrib.get("height", 0))

        if w <= 0 or h <= 0:
            return
        rx_str = tag.get('rx')
        ry_str = tag.get('ry')
        if rx_str is not None or ry_str is not None:
            if ry_str is None:
                ry_str = rx_str
            elif rx_str is None:
                rx_str = ry_str
            assert rx_str is not None and ry_str is not None
            rx = float(rx_str)
            ry = float(ry_str)
            if rx > w / 2:
                rx = w / 2
            if ry > h / 2:
                ry = h / 2
        else:
            rx = 0.0
            ry = 0.0

        if rx > 0 and ry > 0:
            r = complex(rx, ry)
            paths.addArc(complex(x+w-rx, y), complex(x+w, y+ry), 0, r)
            paths.addLine(complex(x+w, y+ry), complex(x+w, y+h-ry))
            paths.addArc(complex(x+w, y+h-ry), complex(x+w-rx, y+h), 0, r)
            paths.addLine(complex(x+w-rx, y+h), complex(x+rx, y+h))
            paths.addArc(complex(x+rx, y+h), complex(x, y+h-ry), 0, r)
            paths.addLine(complex(x, y+h-ry), complex(x, y+ry))
            paths.addArc(complex(x, y+ry), complex(x+rx, y), 0, r)
            paths.addLine(complex(x+rx, y), complex(x+w-rx, y))
        else:
            paths.addLine(complex(x+w, y), complex(x+w, y+h))
            paths.addLine(complex(x+w, y+h), complex(x, y+h))
            paths.addLine(complex(x, y+h), complex(x, y))
            paths.addLine(complex(x, y), complex(x+w, y))

    def __processPathTag(self, tag: ElementTree.Element, node: DocumentVectorNode) -> None:
        paths = node.getPaths()
        path_string = tag.attrib.get("d", "").replace(",", " ")
        start = None
        p0 = complex(0, 0)
        cp1 = complex(0, 0)
        for command in re.findall("[a-df-zA-DF-Z][^a-df-zA-DF-Z]*", path_string):
            params = list(map(float, re.findall("[-\\+]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?", command[1:])))
            command = command[0]
            if command == "M":
                p0 = complex(params[0], params[1])
                if start is None:
                    start = p0
                for n in range(2, len(params), 2):
                    p1 = complex(params[n], params[n + 1])
                    paths.addLine(p0, p1)
                    p0 = p1
            elif command == "m":
                p0 += complex(params[0], params[1])
                if start is None:
                    start = p0
                for n in range(2, len(params), 2):
                    p1 = p0 + complex(params[n], params[n + 1])
                    paths.addLine(p0, p1)
                    p0 = p1
            elif command == "L":
                for n in range(0, len(params), 2):
                    p1 = complex(params[n], params[n + 1])
                    paths.addLine(p0, p1)
                    p0 = p1
            elif command == "l":
                for n in range(0, len(params), 2):
                    if n + 1 == len(params):
                        p1 = p0 + complex(params[n], 0)
                    else:
                        p1 = p0 + complex(params[n], params[n + 1])
                    paths.addLine(p0, p1)
                    p0 = p1
            elif command == 'H':
                p1 = complex(params[0], p0.imag)
                paths.addLine(p0, p1)
                p0 = p1
            elif command == 'h':
                p1 = p0 + complex(params[0], 0)
                paths.addLine(p0, p1)
                p0 = p1
            elif command == 'V':
                p1 = complex(p0.real, params[0])
                paths.addLine(p0, p1)
                p0 = p1
            elif command == 'v':
                p1 = p0 + complex(0, params[0])
                paths.addLine(p0, p1)
                p0 = p1
            elif command == 'A':
                while len(params) > 6:
                    p1 = complex(params[5], params[6])
                    paths.addArc(p0, p1, params[2], complex(params[0], params[1]), large_arc=params[3] > 0, sweep=params[4] <= 0)
                    params = params[7:]
                    p0 = p1
            elif command == 'a':
                while len(params) > 6:
                    p1 = p0 + complex(params[5], params[6])
                    paths.addArc(p0, p1, params[2], complex(params[0], params[1]), large_arc=params[3] > 0, sweep=params[4] <= 0)
                    params = params[7:]
                    p0 = p1
            elif command == 'c':
                while len(params) > 5:
                    cp0 = p0 + complex(params[0], params[1])
                    cp1 = p0 + complex(params[2], params[3])
                    p1 = p0 + complex(params[4], params[5])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[6:]
            elif command == 'C':
                while len(params) > 5:
                    cp0 = complex(params[0], params[1])
                    cp1 = complex(params[2], params[3])
                    p1 = complex(params[4], params[5])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[6:]
            elif command == 's':
                while len(params) > 3:
                    cp0 = p0 - (cp1 - p0)
                    cp1 = p0 + complex(params[0], params[1])
                    p1 = p0 + complex(params[2], params[3])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[4:]
            elif command == 'S':
                while len(params) > 3:
                    cp0 = p0 - (cp1 - p0)
                    cp1 = complex(params[0], params[1])
                    p1 = complex(params[2], params[3])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[4:]
            elif command == 'q':
                while len(params) > 3:
                    cp0 = p0 + complex(params[0], params[1])
                    cp1 = cp0
                    p1 = p0 + complex(params[2], params[3])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[4:]
            elif command == 'Q':
                while len(params) > 3:
                    cp0 = complex(params[0], params[1])
                    cp1 = cp0
                    p1 = complex(params[2], params[3])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[4:]
            elif command == 't':
                while len(params) > 1:
                    cp0 = p0 - (cp1 - p0)
                    cp1 = cp0
                    p1 = p0 + complex(params[0], params[1])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[2:]
            elif command == 'T':
                while len(params) > 1:
                    cp0 = p0 - (cp1 - p0)
                    cp1 = cp0
                    p1 = complex(params[0], params[1])
                    paths.addCurve(p0, p1, cp0, cp1)
                    p0 = p1
                    params = params[2:]
            elif command == "Z" or command == "z":
                if p0 is not None and start is not None:
                    paths.addLine(p0, start)
                start = None
            else:
                logging.warning("Unknown path command: %s %s", command, params)

    def __pushTransform(self, transform: str) -> None:
        t = ComplexTransform()
        for match in re.finditer("([a-z]+)\\(([^\\)]*)\\)", transform.lower()):
            func, params_str = match.groups()
            params = list(map(float, re.findall("-?[0-9]+(?:\\.[0-9]*)?(?:[eE][+-]?[0-9]+)?", params_str)))
            if func == "translate" and len(params) > 1:
                t = ComplexTransform.translate(complex(params[0], params[1])).combine(t)
            elif func == "rotate" and len(params) == 1:
                t = ComplexTransform.rotate(params[0]).combine(t)
            elif func == "rotate" and len(params) == 3:
                offset = complex(params[1], params[2])
                t = ComplexTransform.translate(offset).combine(ComplexTransform.rotate(params[0]).combine(ComplexTransform.translate(-offset).combine(t)))
            elif func == "scale" and len(params) == 1:
                t = ComplexTransform.scale(complex(params[0], params[0])).combine(t)
            elif func == "scale" and len(params) > 1:
                t = ComplexTransform.scale(complex(params[0], params[1])).combine(t)
            elif func == "matrix" and len(params) == 6:
                t = ComplexTransform([params[0], params[2], params[4], params[1], params[3], params[5], 0.0, 0.0, 1.0]).combine(t)
            elif func == "skewx" and len(params) == 1:
                t = ComplexTransform([1.0, math.tan(math.radians(params[0])), 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]).combine(t)
            elif func == "skewy" and len(params) == 1:
                t = ComplexTransform([1.0, 0.0, 0.0, math.tan(math.radians(params[0])), 1.0, 0.0, 0.0, 0.0, 1.0]).combine(t)
            else:
                logging.warning("Ignoring transform: %s %s", func, params)
        self.__transform_stack.append(t.combine(self.__transform_stack[-1]))

    def __getNodeFor(self, tag: ElementTree.Element, base_node: DocumentVectorNode) -> DocumentVectorNode:
        color_name = self.__getColorOf(tag)

        color = None
        if color_name.startswith("#"):
            if len(color_name) == 4:
                color_name = color_name[0:2] + color_name[1] + color_name[2] + color_name[2] + color_name[3] + color_name[3]
            color = int(color_name[1:], 16)

        for child in base_node:
            if child.name == color_name:
                assert isinstance(child, DocumentVectorNode)
                return child
        child = DocumentVectorNode(color_name)
        if color is not None:
            child.color = color
        base_node.append(child)
        child.getPaths().setTransformStack(self.__transform_stack)
        return child

    def __getColorOf(self, tag: ElementTree.Element) -> str:
        # TODO: Color can be inherited from parent nodes, we do not handle this yet.
        style = tag.attrib.get("style", "")
        styles = {}
        for style_part in style.split(";"):
            key, _, value = style_part.partition(":")
            styles[key] = value

        if "stroke" in styles:
            return styles["stroke"]
        elif "fill" in styles:
            return styles["fill"]
        elif "stroke" in tag.attrib:
            return tag.get("stroke") or ""
        elif "fill" in tag.attrib:
            return tag.get("fill") or ""
        return "NoColor"
