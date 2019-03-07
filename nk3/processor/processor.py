import logging
import math
from typing import List

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.processor import pathUtils
from nk3.processor.job import Job
from nk3.processor.pathUtils import Move
from nk3.processor.tabGenerator import TabGenerator


class Processor:
    def __init__(self, job: Job) -> None:
        self.__job = job

    def process(self) -> List[Move]:
        # Process paths with pyclipper (offsets)
        path_tree = self.__process2d()
        # TODO: Calculate problem areas
        # Generate pockets
        self.__processPockets(path_tree)
        # TODO: Order the paths
        path_list = self.__orderPaths(path_tree)
        # Convert 2d paths to 3d paths
        return self.__processToMoves(path_list)

    def __process2d(self) -> pathUtils.Paths:
        if self.__job.settings.cut_offset != 0.0:
            result = self.__job.closedPaths.union()
            if self.__job.openPaths:
                logging.warning("Job has %d open paths, will be ignored...", len(self.__job.openPaths))
            return result.offset(self.__job.settings.cut_offset, tree=True)
        self.__job.closedPaths.combine(self.__job.openPaths)
        for path in self.__job.closedPaths:
            path.removeDuplicates()
        return self.__job.closedPaths

    def __processPockets(self, path_tree: pathUtils.Paths) -> None:
        for paths in DepthFirstIterator(path_tree, include_root=False, iter_function=lambda n: n.children):
            if self.__needPocket(paths):
                # Combine our childs into ourselfs, so the pocket becomes a single Paths group.
                for child in paths.children:
                    paths.combine(child)
                    child.clear()
                prev = paths
                result = prev.offset(-abs(self.__job.settings.pocket_offset))
                while len(result) > 0:
                    paths.addChild(result)
                    prev = result
                    result = prev.offset(-abs(self.__job.settings.pocket_offset))
            elif self.__needTabs(paths):
                for path in paths:
                    path.addTag("tabs")

    def __orderPaths(self, path_tree: pathUtils.Paths) -> List[pathUtils.Path]:
        result = []
        for paths in DepthFirstIterator(path_tree, iter_function=lambda n: n.children):
            for path in paths:
                if path.length() == 0.0:
                    continue
                result.append(path)
        return result

    def __processToMoves(self, path_list: List[pathUtils.Path]) -> List[Move]:
        cut_depth_total = self.__job.settings.cut_depth_total
        cut_depth_pass = self.__job.settings.cut_depth_pass
        if self.__job.settings.attack_angle < 90:
            attack_length = cut_depth_pass / math.tan(math.radians(self.__job.settings.attack_angle))
        else:
            attack_length = 0.0

        depths = [-cut_depth_pass]
        while depths[-1] > -cut_depth_total:
            depths.append(depths[-1] - cut_depth_pass)
        depths[-1] = -cut_depth_total

        moves = [Move(complex(0, 0), self.__job.settings.travel_height, self.__job.settings.travel_speed)]
        for path in path_list:
            if moves[-1].xy is not None:
                path.shiftStartTowards(moves[-1].xy)

            # Add enough cut distance to cut out each depth for the path
            total_distance = 0.0
            path.addDepthAtDistance(0, 0)
            # Note: if the path is shorter then the distance we need to go for the attack, we go the full attack distance for each depth pass.
            #       this generates a nice downwards spiral on small holes
            depth_pass_distance = max(path.length(), attack_length)
            for depth in depths:
                path.addDepthAtDistance(depth, total_distance + attack_length)
                total_distance += depth_pass_distance
                path.addDepthAtDistance(depth, total_distance)

            # Move a bit extra to cut away the attack length at maximum depth.
            if path.closed:
                total_distance += min(path.length(), attack_length)
            elif attack_length > 0.0:
                total_distance += path.length()
            path.addDepthAtDistance(depths[-1], total_distance)

            if path.hasTag("tabs"):
                TabGenerator(self.__job.settings, path)

            moves.append(Move(path[0], self.__job.settings.travel_height, self.__job.settings.travel_speed))
            for point, height in path.iterateDepthPoints():
                moves.append(Move(point, height, self.__job.settings.cut_feedrate))
            moves.append(Move(moves[-1].xy, self.__job.settings.travel_height, self.__job.settings.lift_speed))
        moves.append(Move(complex(0, 0), self.__job.settings.travel_height, self.__job.settings.travel_speed))
        return moves

    def __needPocket(self, paths: pathUtils.Paths) -> bool:
        if self.__job.settings.pocket_offset > 0.0 and not paths.isHole:
            return True
        if self.__job.settings.pocket_offset < 0.0 and paths.isHole:
            return True
        return False

    def __needTabs(self, paths: pathUtils.Paths) -> bool:
        if self.__needPocket(paths):
            return False
        if self.__job.settings.tab_height <= 0.0 or self.__job.settings.pocket_offset > 0.0:
            return False
        for path in paths.offset(-self.__job.settings.tool_diameter):
            if path.length() > 0:
                return True
        return False
