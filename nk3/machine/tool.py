from typing import Dict, List, Type, Optional

from PyQt5.QtCore import pyqtProperty

from nk3.machine.operation import Operation
from nk3.processor.processorSettings import ProcessorSettings
from nk3.qt.QObjectBase import QProperty, qtSlot
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance
from nk3.settingType import SettingType


class Tool(QObjectList[SettingInstance]):
    name = QProperty[str]("?")
    operations = QProperty[QObjectList[Operation]](QObjectList[Operation]("PLACEHOLDER"))

    def __init__(self, settings: Optional[List[SettingType]] = None, operation_types: Optional[List[Type[Operation]]] = None) -> None:
        super().__init__("setting")
        self.operations = QObjectList[Operation]("operation")
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]
        self.__operation_types = operation_types if operation_types is not None else []

        for setting_type in settings if settings is not None else []:
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @qtSlot
    def addOperation(self, operation_name: str) -> None:
        for operation in self.__operation_types:
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

    @pyqtProperty("QStringList", constant=True)
    def operation_types(self) -> List[str]:
        return [operation.DEFAULT_NAME for operation in self.__operation_types]

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        raise NotImplementedError

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
