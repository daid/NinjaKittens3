import logging
import re
import math

from typing import Iterator
from xml.etree import ElementTree

from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.fileReader import FileReader
from nk3.vectorPath.complexTransform import ComplexTransform

log = logging.getLogger(__name__.split(".")[-1])


class SVGFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterator[str]:
        return "svg",

    def __init__(self):
        super().__init__()
        self.__xml = None
        dpi = 90
        self.__transform_stack = [ComplexTransform.scale(complex(25.4/dpi, -25.4/dpi))]

    def load(self, filename: str) -> DocumentNode:
        self.__xml = ElementTree.parse(filename)
        root_node = DocumentVectorNode(filename)
        root_node.getPaths().setTransformStack(self.__transform_stack)
        self.__processGTag(self.__xml.getroot(), root_node)
        root_node.getPaths().stitch()
        return root_node

    def __processGTag(self, tag, node):
        for child in tag:
            if child.get("transform"):
                self.__pushTransform(child.get("transform"))
            child_tag = child.tag[child.tag.find('}') + 1:].lower()
            if child_tag == "g" or child_tag == "a":
                self.__processGTag(child, node)
            elif child_tag == "line":
                self.__processLineTag(child, node)
            elif child_tag == "polyline":
                self.__processPolylineTag(child, node)
            elif child_tag == "polygon":
                self.__processPolygonTag(child, node)
            elif child_tag == "circle":
                self.__processCircleTag(child, node)
            elif child_tag == "ellipse":
                self.__processEllipseTag(child, node)
            elif child_tag == "path":
                self.__processPathTag(child, node)
            elif child_tag == "rect":
                self.__processRectTag(child, node)
            elif child_tag in ("desc", "title", "animate", "animateColor", "animateTransform", "script", "namedview", "metadata"):
                pass  # ignore these tags, as they contain no value for us.
            else:
                log.warning("Unknown svg tag: %s", child_tag)
            if child.get("transform"):
                self.__transform_stack.pop()

    def __processLineTag(self, tag, node):
        x1 = float(tag.get('x1', 0))
        y1 = float(tag.get('y1', 0))
        x2 = float(tag.get('x2', 0))
        y2 = float(tag.get('y2', 0))
        node.getPaths().addLine(complex(x1, y1), complex(x2, y2))

    def __processPolylineTag(self, tag, node):
        paths = node.getPaths()
        values = list(map(float, re.split('[, \t]+', tag.get('points', '').strip())))
        p0 = complex(values[0], values[1])
        for n in range(2, len(values)-1, 2):
            p1 = complex(values[n], values[n + 1])
            paths.addLine(p0, p1)
            p0 = p1

    def __processPolygonTag(self, tag, node):
        paths = node.getPaths()
        values = list(map(float, re.split('[, \t]+', tag.get('points', '').strip())))
        start = p0 = complex(values[0], values[1])
        for n in range(2, len(values)-1, 2):
            p1 = complex(values[n], values[n + 1])
            paths.addLine(p0, p1)
            p0 = p1
        paths.addLine(p0, start)

    def __processCircleTag(self, tag, node):
        cx = float(tag.get('cx', '0'))
        cy = float(tag.get('cy', '0'))
        r = float(tag.get('r', '0'))
        paths = node.getPaths()
        paths.addCircle(complex(cx, cy), r)

    def __processEllipseTag(self, tag, node):
        cx = float(tag.get('cx', '0'))
        cy = float(tag.get('cy', '0'))
        rx = float(tag.get('rx', '0'))
        ry = float(tag.get('ry', '0'))
        paths = node.getPaths()
        paths.addArcByAngle(complex(cx, cy), complex(rx, ry), 0, 360)

    def __processRectTag(self, tag, node):
        paths = node.getPaths()
        x = float(tag.get("x", 0))
        y = float(tag.get("y", 0))
        w = float(tag.get("width", 0))
        h = float(tag.get("height", 0))

        if w <= 0 or h <= 0:
            return
        rx = tag.get('rx')
        ry = tag.get('ry')
        if rx is not None or ry is not None:
            if ry is None:
                ry = rx
            elif rx is None:
                rx = ry
            rx = float(rx)
            ry = float(ry)
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

    def __processPathTag(self, tag, node):
        paths = node.getPaths()
        path_string = tag.get("d", "").replace(",", " ")
        start = None
        p0 = complex(0, 0)
        cp1 = complex(0, 0)
        for command in re.findall("[a-df-zA-DF-Z][^a-df-zA-DF-Z]*", path_string):
            params = list(map(float, re.findall("-?[0-9]+(?:\\.[0-9]*)?(?:[eE][+-]?[0-9]+)?", command[1:])))
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
                log.warning("Unknown path command: %s %s", command, params)

    def __pushTransform(self, transform: str) -> None:
        t = ComplexTransform()
        for match in re.finditer("([a-z]+)\\(([^\\)]*)\\)", transform.lower()):
            func, params = match.groups()
            params = list(map(float, re.findall("-?[0-9]+(?:\\.[0-9]*)?(?:[eE][+-]?[0-9]+)?", params)))
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
                log.warning("Ignoring transform: %s %s", func, params)
        self.__transform_stack.append(t.combine(self.__transform_stack[-1]))
