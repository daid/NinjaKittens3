from nk3.machine.operation import Operation
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType


class CutCenterOperation(Operation):
    DEFAULT_NAME = "Center"

    def __init__(self) -> None:
        super().__init__([
            SettingType(key="cut_depth_total", label="Cut depth", type="dimension", default="6.0",
                        tooltip="""Total depth of cutting into the material."""),
            SettingType(key="tab_height", label="Tab height", type="dimension", default="2.5",
                        tooltip="""Height of the tabs holding target object to the rest of the material.
                        Set to 0.0 to disable the generation of holding tabs."""),
        ])

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        settings.cut_depth_total = float(self.getSettingValue("cut_depth_total"))
        settings.cut_offset = 0.0
        settings.tab_height = float(self.getSettingValue("tab_height"))
