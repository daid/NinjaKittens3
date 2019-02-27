import logging

from PyQt5.QtCore import pyqtProperty

from nk3.machine.operation.jobOperationInstance import JobOperationInstance
from nk3.machine.operation.jobOperationType import JobOperationType
from nk3.processor.settings import Settings

log = logging.getLogger(__name__.split(".")[-1])

from typing import Dict

from nk3.machine.machineType import MachineType
from nk3.QObjectList import QObjectList
from nk3.QObjectBase import QObjectBaseProperty, qtSlot
from nk3.settingInstance import SettingInstance


class MachineInstance(QObjectList):
    name = QObjectBaseProperty(str, "")
    tools = QObjectBaseProperty(QObjectList, None)

    def __init__(self, name: str, machine_type: MachineType) -> None:
        super().__init__("setting")
        self.name = name
        self.tools = QObjectList("tool")
        self.__type = machine_type
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]

        for setting_type in machine_type.getSettingTypes():
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @qtSlot
    def addTool(self, operation: JobOperationType) -> None:
        self.tools.append(JobOperationInstance(self, operation))

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
    def type(self):
        return self.__type

    @pyqtProperty(QObjectList, constant=True)
    def tool_types(self):
        return self.__type.getToolTypes()

    def fillProcessorSettings(self, settings: Settings) -> None:
        self.__type.fillProcessorSettings(self, settings)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value