import logging
import math
from typing import List

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.processor import pathUtils
from nk3.processor.job import Job
from nk3.processor.pathUtils import Move
from nk3.processor.tabGenerator import TabGenerator

log = logging.getLogger(__name__.split(".")[-1])


class Processor:
    def __init__(self, job: Job) -> None:
        self.__job = job
        self.__moves = []

    def process(self):
        # Process paths with pyclipper (offsets)
        path_tree = self.__process2d()
        # TODO: Calculate problem areas
        # Convert 2d paths from pyclipper to 3d paths
        return self.__process2dTo3d(path_tree)

    def __process2d(self) -> pathUtils.Paths:
        if self.__job.settings.cut_offset != 0.0:
            result = self.__job.closedPaths.union()
            if self.__job.openPaths:
                log.warning("Job has open paths, will be ignored...")
            return result.offset(self.__job.settings.cut_offset, tree=True)
        return self.__job.closedPaths.union()

    def __process2dTo3d(self, path_tree: pathUtils.Paths) -> List[Move]:
        cut_depth_total = self.__job.settings.cut_depth_total
        cut_depth_pass = self.__job.settings.cut_depth_pass
        if self.__job.settings.attack_angle < 90:
            attack_length = cut_depth_pass / math.tan(math.radians(self.__job.settings.attack_angle))
        else:
            attack_length = None

        depths = [-cut_depth_pass]
        while depths[-1] > -cut_depth_total:
            depths.append(depths[-1] - cut_depth_pass)
        depths[-1] = -cut_depth_total

        self.__moves.append(Move(None, self.__job.settings.travel_height, self.__job.settings.travel_speed))
        for paths in DepthFirstIterator(path_tree, lambda n: n.children):
            if self.__needPocket(paths):
                if not paths.isHole:
                    for child in paths.children:
                        paths.combine(child)
                        child.clear()
                result = paths.offset(-abs(self.__job.settings.pocket_offset))
                while len(result) > 0:
                    paths.combine(result)
                    result = result.offset(-abs(self.__job.settings.pocket_offset))
            for path in paths:
                f = 0
                path.addDepthAtDistance(0, 0)
                path_length = max(path.length(), attack_length)
                for depth in depths:
                    path.addDepthAtDistance(depth, f + attack_length)
                    f += path_length
                    path.addDepthAtDistance(depth, f)
                f += min(path.length(), attack_length)
                path.addDepthAtDistance(depths[-1], f)

                if self.__needTabs(paths):
                    TabGenerator(self.__job.settings, path)

                self.__moves.append(Move(path[0], self.__job.settings.travel_height, self.__job.settings.travel_speed))
                for point, height in path.iterateDepthPoints():
                    self.__moves.append(Move(point, height, self.__job.settings.cut_feedrate))
                self.__moves.append(Move(self.__moves[-1].xy, self.__job.settings.travel_height, self.__job.settings.lift_speed))
        self.__moves.append(Move(complex(0, 0), self.__job.settings.travel_height, self.__job.settings.travel_speed))
        return self.__moves

    def __needPocket(self, paths: pathUtils.Paths):
        if self.__job.settings.pocket_offset > 0.0 and not paths.isHole:
            return True
        if self.__job.settings.pocket_offset < 0.0 and paths.isHole:
            return True
        return False

    def __needTabs(self, paths):
        if self.__needPocket(paths):
            return False
        if self.__job.settings.tab_height <= 0.0 or self.__job.settings.pocket_offset > 0.0:
            return False
        for path in paths.offset(-self.__job.settings.tool_diameter):
            if path.length() > 0:
                return True
        return False
