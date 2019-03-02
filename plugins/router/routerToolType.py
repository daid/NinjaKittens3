import logging
from typing import TYPE_CHECKING

from nk3.machine.tool.toolType import ToolType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
from .cutCenter import CutCenterOperation
from .cutInside import CutInsideOperation
from .cutOutside import CutOutsideOperation
from .cutOutsideWithPocket import CutOutsideWithPocketOperation
from .cutPocket import CutPocketOperation

if TYPE_CHECKING:
    from nk3.machine.tool.toolInstance import ToolInstance

log = logging.getLogger(__name__.split(".")[-1])


## The RouterTool defines which settings are available for CNC router cutting tools
class RouterToolType(ToolType):
    def __init__(self) -> None:
        super().__init__([
            SettingType(key="tool_diameter", label="Endmill diameter", type="dimension", default="6.0"),
            SettingType(key="cut_depth_pass", label="Cut depth per pass", type="dimension", default="1.0"),
            SettingType(key="cut_feedrate", label="Feedrate", type="speed", default="1200"),
            SettingType(key="plunge_feedrate", label="Plungerate", type="speed", default="180"),
        ], [
            CutOutsideOperation(),
            CutOutsideWithPocketOperation(),
            CutInsideOperation(),
            CutPocketOperation(),
            CutCenterOperation(),
        ])

    def fillProcessorSettings(self, instance: "ToolInstance", settings: Settings) -> None:
        settings.tool_diameter = float(instance.getSettingValue("tool_diameter"))
        settings.cut_depth_pass = float(instance.getSettingValue("cut_depth_pass"))
        settings.cut_feedrate = float(instance.getSettingValue("cut_feedrate"))
        settings.plunge_feedrate = float(instance.getSettingValue("plunge_feedrate"))
