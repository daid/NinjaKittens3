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

    def __process2d(self) -> pathUtils.TreeNode:
        if self.__job.settings.cut_offset != 0.0:
            result = pathUtils.union(self.__job.closedPaths)
            if self.__job.openPaths:
                log.warning("Job has open paths, will be ignored...")
            return pathUtils.offset(result, self.__job.settings.cut_offset, tree=True)
        return self.__job.closedPaths

    def __process2dTo3d(self, path_tree: pathUtils.TreeNode) -> List[Move]:
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
        for node in DepthFirstIterator(path_tree, lambda n: n.children):
            path = node.contour
            max_depth_per_point = [-cut_depth_total] * len(path)
            if self.__needTabs(node):
                TabGenerator(self.__job.settings, path, max_depth_per_point)
            self.__moves.append(Move(path[0], self.__job.settings.travel_height, self.__job.settings.travel_speed))
            for depth in depths:
                if self.__needPocket(node):
                    for p in self.__concentricInfill([path] + [n.contour for n in node.children], self.__job.settings.pocket_offset):
                        # TODO: This assumes we can safely moves to any point in our pocket, which is not always the case.
                        self.__closedPathToMoves(p, depth)
                self.__closedPathToMoves(path, depth, max_depth_per_point=max_depth_per_point, attack_length=attack_length)
            self.__moves.append(Move(path[0], self.__job.settings.travel_height, self.__job.settings.lift_speed))
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

    def __closedPathToMoves(self, path, depth, *, max_depth_per_point=None, attack_length=None):
        depth_list = [depth] * len(path)
        if max_depth_per_point:
            for n in range(len(path)):
                depth_list[n] = max(depth_list[n], max_depth_per_point[n])
        if attack_length:
            path = path.copy()
            while pathUtils.length(path) < attack_length:
                path += path
            pathUtils.insertPoint(attack_length, path, depth_list)
            f = 0
            n = 0
            while f < attack_length:
                depth_list[n] += self.__job.settings.cut_depth_pass * (attack_length - f) / attack_length
                n += 1
                f += abs(path[n % len(path)] - path[n-1])
        self.__moves.append(Move(path[0], depth_list[0], self.__job.settings.plunge_feedrate))
        for point, depth_at_point in zip(path, depth_list):
            self.__moves.append(Move(point, depth_at_point, self.__job.settings.cut_feedrate))
        self.__moves.append(Move(path[0], depth_list[-1], self.__job.settings.cut_feedrate))
