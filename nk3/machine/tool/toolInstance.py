import logging

from PyQt5.QtCore import pyqtProperty

from nk3.machine.operation import Operation
from nk3.processor.processorSettings import ProcessorSettings

log = logging.getLogger(__name__.split(".")[-1])

from typing import Dict, TYPE_CHECKING, List

from nk3.machine.tool.toolType import ToolType
from nk3.qt.QObjectList import QObjectList
from nk3.qt.QObjectBase import QProperty, qtSlot
from nk3.settingInstance import SettingInstance
if TYPE_CHECKING:
    from nk3.machine.machineInstance import MachineInstance


class ToolInstance(QObjectList[SettingInstance]):
    name = QProperty[str]("?")
    operations = QProperty[QObjectList[Operation]](QObjectList[Operation]("PLACEHOLDER"))

    def __init__(self, machine: "MachineInstance", cut_tool_type: ToolType) -> None:
        super().__init__("setting")
        self.operations = QObjectList[Operation]("operation")
        self.__machine = machine
        self.__type = cut_tool_type
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]

        for setting_type in cut_tool_type.getSettingTypes():
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @qtSlot
    def addOperation(self, operation_name: str) -> None:
        for operation in self.__type.getOperationTypes():
            if operation.DEFAULT_NAME == operation_name:
                self.operations.append(operation())

    @qtSlot
    def removeOperation(self, index: int) -> None:
        self.operations.remove(index)

    @qtSlot
    def delete(self) -> None:
        if self.parent().size() < 2:
            return
        for n in range(self.parent().size()):
            if self.parent().get(n) == self:
                self.parent().remove(n)
                return

    @property
    def type(self) -> ToolType:
        return self.__type

    @pyqtProperty("QStringList", constant=True)
    def operation_types(self) -> List[str]:
        return [operation.DEFAULT_NAME for operation in self.__type.getOperationTypes()]

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        self.__machine.fillProcessorSettings(settings)
        self.__type.fillProcessorSettings(self, settings)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
