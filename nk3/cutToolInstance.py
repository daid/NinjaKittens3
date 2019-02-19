import logging

from PyQt5.QtCore import pyqtProperty

from nk3.jobOperationInstance import JobOperationInstance
from nk3.jobOperationType import JobOperationType
from nk3.processor.settings import Settings

log = logging.getLogger(__name__.split(".")[-1])

from typing import Dict

from nk3.cutToolType import CutToolType
from nk3.QObjectList import QObjectList
from nk3.QObjectBase import QObjectBaseProperty, qtSlot
from nk3.settingInstance import SettingInstance


class CutToolInstance(QObjectList):
    name = QObjectBaseProperty(str, "")
    operations = QObjectBaseProperty(QObjectList, None)

    def __init__(self, name: str, cut_tool_type: CutToolType) -> None:
        super().__init__("setting")
        self.name = name
        self.operations = QObjectList("operation")
        self.__type = cut_tool_type
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]

        for setting_type in cut_tool_type.getSettingTypes():
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @qtSlot
    def addOperation(self, operation: JobOperationType) -> None:
        self.operations.append(JobOperationInstance(self, operation))

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
    def type(self):
        return self.__type

    @pyqtProperty(QObjectList, constant=True)
    def operation_types(self):
        return self.__type.getOperationTypes()

    def fillProcessorSettings(self, settings: Settings) -> None:
        self.__type.fillProcessorSettings(self, settings)

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
