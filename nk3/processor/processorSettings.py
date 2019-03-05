import logging

log = logging.getLogger(__name__.split(".")[-1])


class ProcessorSettings:
    def __init__(self) -> None:
        self.tool_diameter = 0.0
        self.cut_offset = 0.0
        self.cut_depth_pass = 1.0
        self.cut_depth_total = 6.0
        self.cut_feedrate = 600.0
        self.plunge_feedrate = 60.0

        self.attack_angle = 0.0

        self.travel_height = 5.0
        self.travel_speed = 1200
        self.lift_speed = 300

        self.pocket_offset = 0.0
        self.tab_height = 0.0
