import logging
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType
from .routerTool import RouterTool
from nk3.machine.machine import Machine

log = logging.getLogger(__name__.split(".")[-1])


class RouterMachine(Machine):
    def __init__(self) -> None:
        super().__init__([
            SettingType(key="attack_angle", label="Attack Angle", type="angle", default="15.0"),
        ], [
            RouterTool
        ])

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        settings.attack_angle = float(self.getSettingValue("attack_angle"))
