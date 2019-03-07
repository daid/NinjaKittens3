import math

from typing import Optional, List


class ComplexTransform:
    def __init__(self, matrix: Optional[List[float]]=None) -> None:
        if matrix is None:
            matrix = [
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0,
            ]
        self.__matrix = matrix

    def __mul__(self, other: complex) -> complex:
        m = self.__matrix
        return complex(other.real * m[0] + other.imag * m[1] + m[2], other.real * m[3] + other.imag * m[4] + m[5])

    def combine(self, other: "ComplexTransform") -> "ComplexTransform":
        m0 = self.__matrix
        m1 = other.__matrix
        return ComplexTransform([
            m0[0] * m1[0] + m0[3] * m1[1] + m0[6] * m1[2],
            m0[1] * m1[0] + m0[4] * m1[1] + m0[7] * m1[2],
            m0[2] * m1[0] + m0[5] * m1[1] + m0[8] * m1[2],

            m0[0] * m1[3] + m0[3] * m1[4] + m0[6] * m1[5],
            m0[1] * m1[3] + m0[4] * m1[4] + m0[7] * m1[5],
            m0[2] * m1[3] + m0[5] * m1[4] + m0[8] * m1[5],

            m0[0] * m1[6] + m0[3] * m1[7] + m0[6] * m1[8],
            m0[1] * m1[6] + m0[4] * m1[7] + m0[7] * m1[8],
            m0[2] * m1[6] + m0[5] * m1[7] + m0[8] * m1[8],
        ])

    def __repr__(self) -> str:
        return str(self.__matrix)

    @staticmethod
    def translate(offset: complex) -> "ComplexTransform":
        return ComplexTransform([1.0, 0.0, offset.real, 0.0, 1.0, offset.imag, 0.0, 0.0, 1.0])

    @staticmethod
    def scale(scale: complex) -> "ComplexTransform":
        return ComplexTransform([scale.real, 0.0, 0, 0.0, scale.imag, 0.0, 0.0, 0.0, 1.0])

    @staticmethod
    def rotate(angle: float) -> "ComplexTransform":
        s = math.sin(math.radians(angle))
        c = math.cos(math.radians(angle))
        return ComplexTransform([
            c, -s, 0.0,
            s, c, 0.0,
            0.0, 0.0, 1.0])
