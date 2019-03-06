import logging
from typing import Dict, List, Type, Optional

from PyQt5.QtCore import pyqtProperty

from nk3.machine.export import Export
from nk3.machine.tool import Tool
from nk3.processor.processorSettings import ProcessorSettings
from nk3.qt.QObjectBase import QProperty, qtSlot
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance
from nk3.settingType import SettingType

log = logging.getLogger(__name__.split(".")[-1])


class Machine(QObjectList[SettingInstance]):
    name = QProperty[str]("Unnamed Machine")
    tools = QProperty[QObjectList[Tool]](QObjectList[Tool]("PLACEHOLDER"))
    export = QProperty[Export](Export())

    def __init__(self, settings: Optional[List[SettingType]] = None, tool_types: Optional[List[Type[Tool]]] = None) -> None:
        super().__init__("setting")
        self.tools = QObjectList[Tool]("tool")
        self.__setting_instances = {}  # type: Dict[str, SettingInstance]
        self.__tool_types = tool_types if tool_types is not None else []

        for setting_type in settings if settings is not None else []:
            instance = SettingInstance(setting_type)
            self.append(instance)
            self.__setting_instances[instance.type.key] = instance

    @qtSlot
    def addTool(self, tool_type_name: str) -> None:
        for tool_type in self.__tool_types:
            if tool_type.__name__ == tool_type_name:
                self.tools.append(tool_type())

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

    @pyqtProperty("QStringList", constant=True)
    def tool_types(self) -> List[str]:
        return [tool_type.__name__ for tool_type in self.__tool_types]

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        raise NotImplementedError

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
