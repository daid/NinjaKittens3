import logging

from typing import List

from nk3.processor import pathUtils

log = logging.getLogger(__name__.split(".")[-1])


class TabGenerator:
    def __init__(self, path: List[complex], max_depth_per_point: List[float]):
        self.__path = path
        self.__max_depth_per_point = max_depth_per_point

        tool_diameter = 3
        self.__tab_height = tool_diameter
        self.__tab_top_width = tool_diameter
        self.__tab_bottom_width = self.__tab_height * 2 + self.__tab_top_width

        self.__generate()

    def __generate(self) -> None:
        length = pathUtils.length(self.__path)
        if length < self.__tab_bottom_width:
            return
        self.__addTab(length / 4)
        if length < self.__tab_bottom_width * 2:
            return
        self.__addTab(length / 4 * 3)

    def __addTab(self, offset: float) -> None:
        if offset < self.__tab_bottom_width / 2.0:
            offset += pathUtils.length(self.__path)

        bottom_start = offset - self.__tab_bottom_width / 2.0
        bottom_end = offset + self.__tab_bottom_width / 2.0
        top_start = offset - self.__tab_top_width / 2.0
        top_end = offset + self.__tab_top_width/ 2.0
        self.__ensurePointAt(bottom_start)
        self.__ensurePointAt(bottom_end)
        self.__ensurePointAt(top_start)
        self.__ensurePointAt(top_end)

        a = 0.0
        p0 = None
        for repeat in range(2):
            for n in range(0, len(self.__path)):
                p1 = self.__path[n]
                if p0 is not None:
                    a += abs(p0 - p1)
                    if bottom_start <= a <= top_start:
                        self.__max_depth_per_point[n] += self.__tab_height * (a - bottom_start) / (self.__tab_bottom_width - self.__tab_top_width) * 2
                    elif top_start <= a <= top_end:
                        self.__max_depth_per_point[n] += self.__tab_height
                    elif top_end <= a <= bottom_end:
                        self.__max_depth_per_point[n] += self.__tab_height * -(a - bottom_end) / (self.__tab_bottom_width - self.__tab_top_width) * 2
                    elif a >= bottom_end:
                        return
                p0 = p1

    def __ensurePointAt(self, offset: float) -> None:
        a = 0.0
        p0 = None
        for repeat in range(2):
            for n in range(0, len(self.__path)):
                p1 = self.__path[n]
                if p0 is not None:
                    step = abs(p0 - p1)
                    if a + step > offset:
                        self.__path.insert(n, p0 + (p1 - p0) / step * (offset - a))
                        self.__max_depth_per_point.insert(n, self.__max_depth_per_point[n])
                        return
                    a += step
                p0 = p1
