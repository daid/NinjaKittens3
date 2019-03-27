from nk3.processor.result import Move


class GCodeDialect:
    NAME = "UNKNOWN"

    _NUMBER_FORMAT = "%.4f"

    def convertMove(self, move: Move) -> str:
        raise NotImplementedError

    def _toCompactNumber(self, number: float) -> str:
        return (self._NUMBER_FORMAT % (number)).rstrip("0").rstrip(".")
