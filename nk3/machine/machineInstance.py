import logging
from typing import Dict

from PyQt5.QtCore import pyqtProperty

from nk3.machine.export import Export
from nk3.machine.machineType import MachineType
from nk3.machine.tool.toolInstance import ToolInstance
from nk3.machine.tool.toolType import ToolType
from nk3.processor.settings import Settings
from nk3.qt.QObjectBase import QProperty, qtSlot
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance

log = logging.getLogger(__name__.split(".")[-1])


class MachineInstance(QObjectList[SettingInstance]):
    name = QProperty[str]("")
    tools = QProperty[QObjectList[ToolInstance]](QObjectList[ToolInstance]("PLACEHOLDER"))
    export = QProperty[Export](Export([]))

    def __init__(self, name: str, machine_type: MachineType) -> None:
        super().__init__("setting")
        self.name = name
        self.tools = QObjectList[ToolInstance]("tool")
        self.__type = machine_type
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]

        for setting_type in machine_type.getSettingTypes():
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @qtSlot
    def addTool(self, tool_type: ToolType) -> None:
        self.tools.append(ToolInstance(self, tool_type))

    @qtSlot
    def removeTool(self, index: int) -> None:
        self.tools.remove(index)

    @qtSlot
    def delete(self) -> None:
        if self.parent().size() < 2:
            return
        for n in range(self.parent().size()):
            if self.parent().get(n) == self:
                self.parent().remove(n)
                return

    @property
    def type(self) -> MachineType:
        return self.__type

    @pyqtProperty(QObjectList, constant=True)
    def tool_types(self) -> QObjectList[ToolType]:
        return self.__type.getToolTypes()

    def fillProcessorSettings(self, settings: Settings) -> None:
        self.__type.fillProcessorSettings(self, settings)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
