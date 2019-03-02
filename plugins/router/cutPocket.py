from nk3.machine.operation.jobOperationInstance import JobOperationInstance
from nk3.machine.operation.jobOperationType import JobOperationType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType


class CutPocketOperation(JobOperationType):
    def __init__(self) -> None:
        super().__init__("Pocket", [
            SettingType(key="cut_depth_total", label="Cut depth", type="dimension", default="6.0"),
            SettingType(key="pocket_overlap", label="Pocket overlap", type="percentage", default="50"),
        ])

    def fillProcessorSettings(self, instance: JobOperationInstance, settings: Settings) -> None:
        settings.cut_depth_total = float(instance.getSettingValue("cut_depth_total"))
        settings.cut_offset = -settings.tool_diameter / 2.0
        settings.pocket_offset = settings.tool_diameter * (100 - float(instance.getSettingValue("pocket_overlap"))) / 100.0
