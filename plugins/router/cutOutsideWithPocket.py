from nk3.machine.operation import Operation
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType


class CutOutsideWithPocketOperation(Operation):
    DEFAULT_NAME = "Outside+Pocket"

    def __init__(self) -> None:
        super().__init__([
            SettingType(key="cut_depth_total", label="Cut depth", type="dimension", default="6.0",
                        tooltip="""Total depth of cutting into the material."""),
            SettingType(key="pocket_overlap", label="Pocket overlap", type="percentage", default="50",
                        tooltip="""Percentual overlap of pocket passes, 0% makes each pass cut 100% new material.
                        50% is a decent compromise between speed and cutting quality."""),
            SettingType(key="tab_height", label="Tab height", type="dimension", default="2.5",
                        tooltip="""Height of the tabs holding target object to the rest of the material.
                        Set to 0.0 to disable the generation of holding tabs."""),
        ])

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        settings.cut_depth_total = float(self.getSettingValue("cut_depth_total"))
        settings.cut_offset = settings.tool_diameter / 2.0
        settings.pocket_offset = -settings.tool_diameter * (100 - float(self.getSettingValue("pocket_overlap"))) / 100.0
        settings.tab_height = float(self.getSettingValue("tab_height"))
