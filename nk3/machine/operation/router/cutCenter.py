from nk3.machine.operation.jobOperationInstance import JobOperationInstance
from nk3.machine.operation.jobOperationType import JobOperationType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
import logging

log = logging.getLogger(__name__.split(".")[-1])


class CutCenterOperation(JobOperationType):
    def __init__(self) -> None:
        super().__init__("Center", [
            SettingType(key="cut_depth_total", label="Cut depth", type="dimension", default="6.0"),
            SettingType(key="tab_height", label="Tab height", type="dimension", default="2.5"),
        ])

    def fillProcessorSettings(self, instance: "JobOperationInstance", settings: Settings) -> None:
        settings.cut_depth_total = float(instance.getSettingValue("cut_depth_total"))
        settings.cut_offset = 0.0
        settings.tab_height = float(instance.getSettingValue("tab_height"))
