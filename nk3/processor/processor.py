import logging

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

    def __process2d(self):
        if self.__job.settings.cut_offset != 0.0:
            result = pathUtils.union(self.__job.closedPaths)
            if self.__job.openPaths:
                log.warning("Job has open paths, will be ignored...")
            return pathUtils.offset(result, self.__job.settings.cut_offset, tree=True)
        return self.__job.closedPaths

    def __process2dTo3d(self, path_tree):
        cut_depth_total = self.__job.settings.cut_depth_total
        cut_depth_pass = self.__job.settings.cut_depth_pass
        depths = [-cut_depth_pass]
        while depths[-1] > -cut_depth_total:
            depths.append(depths[-1] - cut_depth_pass)
        depths[-1] = -cut_depth_total

        self.__moves.append(Move(None, self.__job.settings.travel_height, self.__job.settings.travel_speed))
        for node in DepthFirstIterator(path_tree, lambda n: n.children):
            path = node.contour
            max_depth_per_point = [-cut_depth_total] * len(path)
            if self.__needTabs(node):
                TabGenerator(self.__job.settings, path, max_depth_per_point)
            self.__moves.append(Move(path[-1], self.__job.settings.travel_height, self.__job.settings.travel_speed))
            for depth in depths:
                if self.__needPocket(node):
                    for p in self.__concentricInfill([path] + [n.contour for n in node.children], self.__job.settings.pocket_offset):
                        # TODO: This assumes we can safely moves to any point in our pocket, which is not always the case.
                        self.__closedPathToMoves(p, depth)
                self.__closedPathToMoves(path, depth, max_depth_per_point)
            self.__moves.append(Move(path[-1], self.__job.settings.travel_height, self.__job.settings.lift_speed))
        self.__moves.append(Move(complex(0, 0), self.__job.settings.travel_height, self.__job.settings.travel_speed))
        return self.__moves

    def __needPocket(self, node):
        if self.__job.settings.pocket_offset > 0.0 and not node.hole:
            return True
        if self.__job.settings.pocket_offset < 0.0 and node.hole:
            return True
        return False

    def __needTabs(self, node):
        if self.__needPocket(node):
            return False
        if self.__job.settings.tab_height <= 0.0 or self.__job.settings.pocket_offset > 0.0:
            return False
        return len(pathUtils.offset([node.contour], -self.__job.settings.tool_diameter)) > 0

    def __concentricInfill(self, paths, offset):
        result = pathUtils.offset(paths, -abs(offset))
        if len(result) > 0:
            return self.__concentricInfill(result, offset) + result
        return []

    def __closedPathToMoves(self, path, depth, max_depth_per_point=None):
        if max_depth_per_point is None:
            self.__moves.append(Move(path[-1], depth, self.__job.settings.plunge_feedrate))
            for point in path:
                self.__moves.append(Move(point, depth, self.__job.settings.cut_feedrate))
        else:
            self.__moves.append(Move(path[-1], max(depth, max_depth_per_point[-1]), self.__job.settings.plunge_feedrate))
            for point, max_depth in zip(path, max_depth_per_point):
                self.__moves.append(Move(point, max(depth, max_depth), self.__job.settings.cut_feedrate))
