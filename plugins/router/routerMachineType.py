import logging
from typing import TYPE_CHECKING

from nk3.machine.machineType import MachineType
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
from .routerToolType import RouterToolType

if TYPE_CHECKING:
    from nk3.machine.machineInstance import MachineInstance

log = logging.getLogger(__name__.split(".")[-1])


class RouterMachineType(MachineType):
    def __init__(self) -> None:
        super().__init__([
            SettingType(key="attack_angle", label="Attack Angle", type="angle", default="15.0"),
        ], [
            RouterToolType()
        ])

    def fillProcessorSettings(self, instance: "MachineInstance", settings: Settings) -> None:
        settings.attack_angle = float(instance.getSettingValue("attack_angle"))
