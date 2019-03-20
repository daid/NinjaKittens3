import logging
import math
from typing import List, Optional

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.processor import pathUtils
from nk3.processor.job import Job
from nk3.processor.result import Result
from nk3.processor.tabGenerator import TabGenerator


class Processor:
    def __init__(self, job: Job) -> None:
        self.__job = job

    def process(self, result: Result) -> None:
        # Process paths with pyclipper (offsets)
        path_tree = self.__process2d(result)
        # Generate pockets
        self.__processPockets(path_tree)
        path_list = self.__orderPaths(path_tree)
        # Convert 2d paths to 3d paths
        self.__processToMoves(path_list, result)

    def __process2d(self, result: Result) -> pathUtils.Paths:
        if self.__job.settings.cut_offset != 0.0:
            paths = self.__job.closedPaths.union()
            if self.__job.openPaths:
                logging.warning("Job has %d open paths, will be ignored...", len(self.__job.openPaths))
            offset_result = paths.offset(self.__job.settings.cut_offset, tree=True)
            # Calculate problem areas
            if self.__job.settings.cut_offset < 0.0:
                result.addProblemRegions(offset_result.offset(-self.__job.settings.cut_offset + 0.05))
            else:
                result.addProblemRegions(offset_result.offset(-self.__job.settings.cut_offset - 0.05).difference(paths))
            return offset_result
        self.__job.closedPaths.combine(self.__job.openPaths)
        for path in self.__job.closedPaths:
            path.removeDuplicates()
        return self.__job.closedPaths

    def __processPockets(self, path_tree: pathUtils.Paths) -> None:
        for paths in DepthFirstIterator(path_tree, include_root=False, iter_function=lambda n: n.children):
            if self.__needPocket(paths):
                # Combine our childs into ourselves, so the pocket becomes a single Paths group.
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
        pick_list = []
        for paths in DepthFirstIterator(path_tree, iter_function=lambda n: n.children):
            for path in paths:
                if path.length() == 0.0:
                    continue
                pick_list.append(path)
        result = []
        p0 = complex(0, 0)
        while len(pick_list) > 0:
            best_index = None  # type: Optional[int]
            best_distance = 0.0
            for index in range(0, len(pick_list)):
                distance = abs(pick_list[index][0] - p0)
                if best_index is None or distance < best_distance:
                    best_index = index
                    best_distance = distance
            assert best_index is not None
            result.append(pick_list.pop(best_index))
        return result

    def __processToMoves(self, path_list: List[pathUtils.Path], result: Result) -> None:
        cut_depth_total = self.__job.settings.cut_depth_total
        cut_depth_pass = self.__job.settings.cut_depth_pass
        if 0.0 < self.__job.settings.attack_angle < 90.0:
            attack_length = cut_depth_pass / math.tan(math.radians(self.__job.settings.attack_angle))
        else:
            attack_length = 0.0

        depths = [-cut_depth_total]
        while depths[0] < 0:
            depths.insert(0, depths[0] + cut_depth_pass)
        depths.pop(0)

        result.setSpeeds(
            xy_speed=self.__job.settings.cut_feedrate,
            xy_travel_speed=self.__job.settings.travel_speed,
            z_up_speed=self.__job.settings.lift_speed,
            z_down_speed=self.__job.settings.plunge_feedrate
        )

        if result.getLastXY() is None:
            result.addTravel(complex(0, 0), self.__job.settings.travel_height)
        for path in path_list:
            last_xy = result.getLastXY()
            if last_xy is not None:
                path.shiftStartTowards(last_xy)

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

            # Finally, move upwards diagonally if we have an requested attack angle.
            if attack_length > 0.0:
                total_distance += abs(depths[-1]) / math.tan(math.radians(self.__job.settings.attack_angle))
                path.addDepthAtDistance(0.0, total_distance)

            if path.hasTag("tabs"):
                TabGenerator(self.__job.settings, path)

            result.addTravel(path[0], self.__job.settings.travel_height)
            for point, height in path.iterateDepthPoints():
                result.addMove(point, height)
            last_xy = result.getLastXY()
            assert last_xy is not None
            result.addTravel(last_xy, self.__job.settings.travel_height)
        result.addTravel(complex(0, 0), self.__job.settings.travel_height)

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
