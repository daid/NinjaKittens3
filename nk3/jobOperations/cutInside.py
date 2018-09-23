from nk3.jobOperationType import JobOperationType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
import logging

log = logging.getLogger(__name__.split(".")[-1])


class CutInsideOperation(JobOperationType):
    def __init__(self):
        super().__init__("Inside", [
            SettingType(key="cut_depth_total", label="Cut depth", type="dimension", default="6.0"),
        ])

    def fillProcessorSettings(self, instance: "JobOperationInstance", settings: Settings) -> None:
        settings.cut_depth_total = float(instance.getSettingValue("cut_depth_total"))
        settings.cut_offset = -settings.tool_diameter / 2.0
