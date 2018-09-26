import logging
from typing import List

log = logging.getLogger(__name__.split(".")[-1])


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
