import cmath
import math
from typing import Optional, List, Iterator

from nk3.vectorPath.complexTransform import ComplexTransform
from nk3.vectorPath.nurbs import NURBS
from nk3.vectorPath.vectorPath import VectorPath


class VectorPaths:
    __RESOLUTION = 0.5

    def __init__(self) -> None:
        self.__paths = []  # type: List[VectorPath]
        self.__transform_stack = [ComplexTransform()]  # type: List[ComplexTransform]

    def setTransformStack(self, stack: List[ComplexTransform]) -> None:
        self.__transform_stack = stack

    def addLine(self, start: complex, end: complex) -> None:
        self._findOrCreateWithEndPoint(self.__transform_stack[-1] * start).add(self.__transform_stack[-1] * end)

    def addArc(self, start: complex, end: complex, rotation: float, radius: complex, *, large_arc: bool=False, sweep: bool=False) -> None:
        if radius.real == 0.0 or radius.imag == 0.0:
            return self.addLine(start, end)
        if start == end:
            return

        radius = complex(abs(radius.real), abs(radius.imag))
        half_dist = (end - start) / 2.0
        cos_angle = math.cos(math.radians(rotation))
        sin_angle = math.sin(math.radians(rotation))

        # Step 1 : Compute (x1, y1)
        # pos1 = half_dist * cmath.rect(1, math.radians(rotation))
        x1 = cos_angle * half_dist.real + sin_angle * half_dist.imag
        y1 = -sin_angle * half_dist.real + cos_angle * half_dist.imag

        # Ensure radii are large enough
        Prx = radius.real * radius.real
        Pry = radius.imag * radius.imag
        Px1 = x1 * x1
        Py1 = y1 * y1
        # check that radii are large enough
        radii_check = Px1 / Prx + Py1 / Pry
        if radii_check > 1:
            radius = radius * math.sqrt(radii_check)
            Prx = radius.real * radius.real
            Pry = radius.imag * radius.imag

        # Step 2 : Compute (cx1, cy1)
        sq = ((Prx*Pry)-(Prx*Py1)-(Pry*Px1)) / ((Prx*Py1)+(Pry*Px1))
        sq = max(0.0, sq)
        coef = math.sqrt(sq)
        if large_arc == sweep:
            coef = -coef
        cx1 = coef * ((radius.real * y1) / radius.imag)
        cy1 = coef * -((radius.imag * x1) / radius.real)

        # Step 3 : Compute (cx, cy) from (cx1, cy1)
        s = (end + start) / 2.0
        cx = s.real + (cos_angle * cx1 - sin_angle * cy1)
        cy = s.imag + (sin_angle * cx1 + cos_angle * cy1)

        # Step 4 : Compute the angleStart (angle1) and the angleExtent (dangle)
        ux = (x1 - cx1) / radius.real
        uy = (y1 - cy1) / radius.imag
        vx = (-x1 - cx1) / radius.real
        vy = (-y1 - cy1) / radius.imag
        # Compute the angle start
        n = math.sqrt((ux * ux) + (uy * uy))
        p = ux  # (1 * ux) + (0 * uy)
        angle_start = math.degrees(math.acos(p / n))
        if uy < 0:
            angle_start = -angle_start

        # Compute the angle extent
        n = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
        p = ux * vx + uy * vy
        angle_extent = math.degrees(math.acos(p / n))
        if ux * vy - uy * vx < 0:
            angle_extent = -angle_extent
        if not sweep and angle_extent > 0.0:
            angle_extent -= 360.0
        elif sweep and angle_extent < 0.0:
            angle_extent += 360.0

        self.addArcByAngle(complex(cx, cy), radius, angle_start, angle_start + angle_extent, rotation=rotation)

    def addArcByAngle(self, center: complex, radius: complex, start_angle: float, end_angle: float, *, rotation: float=0.0) -> None:
        point_count = math.ceil((abs(start_angle - end_angle) / 180 * math.pi * max(radius.real, radius.imag)) / self.__RESOLUTION)
        path = None
        c = cmath.rect(1.0, math.radians(rotation))
        for n in range(point_count + 1):
            angle = math.radians(start_angle + (end_angle - start_angle) * (n / point_count))
            p = center + complex(math.cos(angle) * radius.real, math.sin(angle) * radius.imag) * c
            if path is None:
                path = self._findOrCreateWithEndPoint(self.__transform_stack[-1] * p)
            else:
                path.add(self.__transform_stack[-1] * p)

    def addCircle(self, center: complex, radius: float) -> None:
        point_count = math.ceil((2.0 * math.pi * radius) / self.__RESOLUTION)
        path = self._createPath()
        for n in range(point_count):
            angle = math.pi * 2.0 * n / point_count
            path.add(self.__transform_stack[-1] * (center + complex(math.cos(angle) * radius, math.sin(angle) * radius)))
        path.close()

    def addBulgeLine(self, start: complex, end: complex, bulge: float) -> None:
        radius = (abs(end - start) / 2) / math.sin(2 * math.atan(bulge))
        self.addArc(start, end, 0, complex(radius, radius), large_arc=False, sweep=bulge < 0)

    def addNurbs(self, nurbs: NURBS) -> None:
        points = nurbs.calculate(nurbs.pointCount())
        distance = 0.0
        for p0, p1 in zip(points[0:-1], points[1:]):
            distance += abs(self.__transform_stack[-1] * p1 - self.__transform_stack[-1] * p0)
        if distance < 1.0:
            point_count = int(max(2, distance / 0.1))
        elif distance < 5.0:
            point_count = int(max(2, distance / 0.3))
        else:
            point_count = int(max(2, distance / 0.5))
        points = nurbs.calculate(point_count)
        p = self._findOrCreateWithEndPoint(self.__transform_stack[-1] * points[0])
        for point in points[1:]:
            p.add(self.__transform_stack[-1] * point)

    def addCurve(self, start: complex, end: complex, cp0: complex, cp1: complex) -> None:
        n = NURBS(3)
        n.addPoint(start)
        n.addPoint(cp0)
        n.addPoint(cp1)
        n.addPoint(end)
        n.addKnot(0)
        n.addKnot(0)
        n.addKnot(0)
        n.addKnot(0)
        n.addKnot(1)
        n.addKnot(1)
        n.addKnot(1)
        n.addKnot(1)
        self.addNurbs(n)

    def _createPath(self, point: Optional[complex]=None) -> VectorPath:
        path = VectorPath()
        if point is not None:
            path.add(point)
        self.__paths.append(path)
        return path

    def _findOrCreateWithEndPoint(self, point: complex) -> VectorPath:
        for path in self.__paths:
            if not path.closed and abs(path.end - point) < 0.001:
                return path
        for path in self.__paths:
            if not path.closed and abs(path.start - point) < 0.001:
                path.reverse()
                return path
        return self._createPath(point)

    def stitch(self) -> None:
        for path in self.__paths:
            if not path.empty and not path.closed:
                while self._stitch(path):
                    pass
        self.__paths = list(filter(lambda path: not path.empty, self.__paths))

    def _stitch(self, source: VectorPath) -> bool:
        if abs(source.start - source.end) < 0.001:
            source.close()
            return False
        for target in self.__paths:
            if target.empty or target.closed or target == source:
                continue
            if abs(source.end - target.start) < 0.001:
                source.join(target)
                return True
            if abs(source.end - target.end) < 0.001:
                target.reverse()
                source.join(target)
                return True
        if abs(source.start - source.end) < 0.001:
            source.close()
        return False

    def __iter__(self) -> Iterator[VectorPath]:
        return iter(self.__paths)

    def debugExport(self, filename: str) -> None:
        f = open(filename, "wt")
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
        f.write("<svg>\n")
        for path in self.__paths:
            f.write("<path style=\"stroke:#000000;stroke-width:0.1;fill:none\" d=\"M")
            for point in path:
                f.write(" %f %f" % (point.real, point.imag))
            if path.closed:
                f.write("Z")
            f.write("\" />\n")
        f.write("</svg>\n")
        f.close()
