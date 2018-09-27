import logging
import re

from typing import Iterator
from xml.etree import ElementTree

from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.fileReader.fileReader import FileReader
from nk3.vectorPath.vectorPaths import VectorPaths
from nk3.vectorPath.complexTransform import ComplexTransform

log = logging.getLogger(__name__.split(".")[-1])


class SVGFileReader(FileReader):
    @staticmethod
    def getExtensions() -> Iterator[str]:
        return "svg",

    def __init__(self):
        super().__init__()
        self.__xml = None

    def load(self, filename: str) -> DocumentNode:
        f = open(filename, "r")
        self.__xml = ElementTree.parse(f)
        root_node = DocumentVectorNode(filename)
        self.__processGTag(self.__xml.getroot(), root_node)
        f.close()
        root_node.getPaths().stitch()
        return root_node

    def __processGTag(self, tag, node):
        for child in tag:
            if child.get("transform"):
                log.warning("Ignoring transform: %s", child.get("transform"))
            child_tag = child.tag[child.tag.find('}') + 1:].lower()
            if child_tag == "g":
                self.__processGTag(child, node)
            elif child_tag == "path":
                self.__processPathTag(child, node)
            else:
                log.warning("Unknown svg tag: %s", child_tag)

    def __processPathTag(self, tag, node):
        paths = node.getPaths()
        path_string = tag.get("d", "").replace(",", " ")
        start = None
        p0 = complex(0, 0)
        cp1 = complex(0, 0)
        for command in re.findall("[a-df-zA-DF-Z][^a-df-zA-DF-Z]*", path_string):
            params = re.findall("-?[0-9]+(?:\\.[0-9]*)?", command[1:])
            params = list(map(float, params))
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
                    paths.addArc(p0, p1, params[2], complex(params[0], params[1]), large_arc=params[3] > 0, sweep=params[4] > 0)
                    params = params[7:]
                    p0 = p1
            elif command == 'a':
                while len(params) > 6:
                    p1 = p0 + complex(params[5], params[6])
                    paths.addArc(p0, p1, params[2], complex(params[0], params[1]), large_arc=params[3] > 0, sweep=params[4] > 0)
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
