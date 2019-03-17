from typing import Dict, List, Type, Optional

from PyQt5.QtCore import pyqtProperty

from nk3.machine.outputmethod import OutputMethod
from nk3.machine.tool import Tool
from nk3.pluginRegistry import PluginRegistry
from nk3.processor.processorSettings import ProcessorSettings
from nk3.qt.QObjectBase import QProperty, qtSlot
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance
from nk3.settingType import SettingType


class Machine(QObjectList[SettingInstance]):
    name = QProperty[str]("Unnamed Machine")
    tools = QProperty[QObjectList[Tool]](QObjectList[Tool]("PLACEHOLDER"))
    output_method = QProperty[OutputMethod](OutputMethod())

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

    @qtSlot
    def switchOutputMethod(self, new_output_method: str) -> None:
        for output_method_type in PluginRegistry.getInstance().getAllClasses(OutputMethod):
            if output_method_type.NAME == new_output_method:
                old_output_method = self.output_method
                old_output_method.release()
                self.output_method = output_method_type()
                for setting in self.output_method:
                    try:
                        setting.value = old_output_method.getSettingValue(setting.type.key)
                    except KeyError:
                        pass
                return

    @pyqtProperty("QStringList", constant=True)
    def tool_types(self) -> List[str]:
        return [tool_type.__name__ for tool_type in self.__tool_types]

    @pyqtProperty("QStringList", constant=True)
    def output_methods(self) -> List[str]:
        return [output_method_type.NAME for output_method_type in PluginRegistry.getInstance().getAllClasses(OutputMethod)]

    def fillProcessorSettings(self, settings: ProcessorSettings) -> None:
        raise NotImplementedError

    def getSettingValue(self, key: str) -> str:
        return self.__setting_instances[key].value
