from nk3.processor.result import Move
from .gcodeDialect import GCodeDialect


class CompatibilityDialect(GCodeDialect):
    NAME = "Compatibility"

    def convertMove(self, move: Move) -> str:
        return "G1 F%d X%f Y%f Z%f" % (move.speed, move.xy.real, move.xy.imag, move.z)
