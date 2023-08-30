from nk3.machine.operation import Operation
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType


class CutSurfaceOperation(Operation):
    DEFAULT_NAME = "Surface"

    def __init__(self) -> None:
        super().__init__([
            SettingType(key="surface_depth", label="Cut depth", type="dimension", default="6.0",
                        tooltip="""Total depth of cutting into the material."""),
            SettingType(key="surface_overlap", label="Overlap", type="percentage", default="50",
                        tooltip="""Percentual overlap of surface passes, 0% makes each pass cut 100% new material.
                        50% is a decent compromise between speed and cutting quality."""),
        ])

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        settings.surface_depth = float(self.getSettingValue("surface_depth"))
        settings.surface_offset = settings.tool_diameter * (100 - float(self.getSettingValue("surface_overlap"))) / 100.0
