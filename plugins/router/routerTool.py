from nk3.machine.tool import Tool
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType
from .cutCenter import CutCenterOperation
from .cutInside import CutInsideOperation
from .cutOutside import CutOutsideOperation
from .cutOutsideWithPocket import CutOutsideWithPocketOperation
from .cutPocket import CutPocketOperation


## The RouterTool defines which settings are available for CNC router cutting tools
class RouterTool(Tool):
    def __init__(self) -> None:
        super().__init__([
            SettingType(key="tool_diameter", label="Endmill diameter", type="dimension", default="6.0"),
            SettingType(key="cut_depth_pass", label="Cut depth per pass", type="dimension", default="1.0"),
            SettingType(key="cut_feedrate", label="Feedrate", type="speed", default="1200"),
            SettingType(key="plunge_feedrate", label="Plungerate", type="speed", default="180"),
        ], [
            CutOutsideOperation,
            CutOutsideWithPocketOperation,
            CutInsideOperation,
            CutPocketOperation,
            CutCenterOperation,
        ])

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        settings.tool_diameter = float(self.getSettingValue("tool_diameter"))
        settings.cut_depth_pass = float(self.getSettingValue("cut_depth_pass"))
        settings.cut_feedrate = float(self.getSettingValue("cut_feedrate"))
        settings.plunge_feedrate = float(self.getSettingValue("plunge_feedrate"))
