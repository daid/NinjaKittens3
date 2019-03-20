import math

from nk3.processor import pathUtils
from nk3.processor.processorSettings import ProcessorSettings


class TabGenerator:
    def __init__(self, settings: ProcessorSettings, path: pathUtils.Path) -> None:
        self.__path = path

        self.__tab_height = settings.tab_height
        self.__tab_top_width = settings.tool_diameter * 1.5
        if 0.0 < settings.attack_angle < 90.0:
            attack_length = self.__tab_height / math.tan(math.radians(settings.attack_angle))
        else:
            attack_length = 0.0001  # The top needs to be slightly smaller then the bottom, else the depthAtDistance of the Path object sorting goes wrong.
        self.__tab_bottom_width = self.__tab_top_width + attack_length * 2

        assert self.__tab_height > 0.0

        self.__generate()

    def __generate(self) -> None:
        length = self.__path.length()
        if length < self.__tab_bottom_width * 4:
            return

        f = length / 3
        if f > self.__tab_bottom_width * 2:
            self.__addTab(self.__findBetterTabOffset(f * 0.5))
            self.__addTab(self.__findBetterTabOffset(f * 1.5))
            self.__addTab(self.__findBetterTabOffset(f * 2.5))
        else:
            self.__addTab(f * 0.5)
            self.__addTab(f * 1.5)
            self.__addTab(f * 2.5)

    def __findBetterTabOffset(self, offset: float) -> float:
        start, end = offset - self.__tab_bottom_width / 2.0, offset + self.__tab_bottom_width / 2.0
        best_score = self.__path.scoreCornering(start, end)
        best_offset = offset
        for n in [-1.0, -0.5, 0.5, 1.0]:
            score = self.__path.scoreCornering(start + self.__tab_bottom_width * n, end + self.__tab_bottom_width * n) + abs(n * 0.001)
            if score < best_score:
                best_score = score
                best_offset = offset + n * self.__tab_bottom_width
        return best_offset

    def __addTab(self, offset: float) -> None:
        max_depth = self.__path.getMaxDepth()
        while offset < self.__path.getTotalDepthDistance():
            bottom_start = offset - self.__tab_bottom_width / 2.0
            bottom_end = offset + self.__tab_bottom_width / 2.0
            top_start = offset - self.__tab_top_width / 2.0
            top_end = offset + self.__tab_top_width / 2.0

            self.__addDepth(bottom_start, max_depth)
            self.__addDepth(bottom_end, max_depth)
            self.__addDepth(top_start, max_depth + self.__tab_height)
            self.__addDepth(top_end, max_depth + self.__tab_height)

            offset += self.__path.length()

    def __addDepth(self, offset: float, depth: float) -> None:
        current_depth = self.__path.getDepthAt(offset)
        depth = max(depth, current_depth)
        if offset > self.__path.getTotalDepthDistance() and depth == current_depth:
            return
        self.__path.addDepthAtDistance(depth, offset)
