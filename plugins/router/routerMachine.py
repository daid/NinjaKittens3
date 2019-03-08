from nk3.machine.machine import Machine
from nk3.processor.processorSettings import ProcessorSettings
from nk3.settingType import SettingType
from .routerTool import RouterTool


class RouterMachine(Machine):
    def __init__(self) -> None:
        super().__init__([
            SettingType(key="travel_feedrate", label="Travel speed", type="speed", default="1200",
                        tooltip="""The speed at which traveling above the workpiece is done"""),
            SettingType(key="attack_angle", label="Attack Angle", type="angle", default="15.0",
                        tooltip="""The worst case angle your tool is allowed to enter the workspace.
                        A lower value gives a shallow entering angle which is better for the tool,
                        as you generally cannot cut straight down properly."""),
        ], [
            RouterTool
        ])

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        settings.travel_speed = float(self.getSettingValue("travel_feedrate"))
        settings.attack_angle = float(self.getSettingValue("attack_angle"))
