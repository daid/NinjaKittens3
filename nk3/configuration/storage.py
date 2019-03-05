import configparser
import logging
import os
import re
from typing import Type, TypeVar, Optional

from nk3.machine.machineInstance import MachineInstance
from nk3.machine.machineType import MachineType
from nk3.machine.operation.jobOperationInstance import JobOperationInstance
from nk3.machine.operation.jobOperationType import JobOperationType
from nk3.machine.tool.toolInstance import ToolInstance
from nk3.machine.tool.toolType import ToolType
from nk3.machine.export import Export
from nk3.pluginRegistry import PluginRegistry
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance

log = logging.getLogger(__name__.split(".")[-1])

T = TypeVar("T")


class Storage:
    def __init__(self) -> None:
        config_base_path = os.environ.get("APPDATA", None)
        if config_base_path is None:
            config_base_path = os.path.expanduser("~/.config")
        self.__configuration_file = os.path.join(config_base_path, "NinjaKittens3", "nk3.conf")

    def load(self, machines: QObjectList[MachineInstance]) -> bool:
        cp = configparser.ConfigParser()
        if not cp.read(self.__configuration_file):
            return False
        for machine_section in filter(lambda key: re.fullmatch("machine_[0-9]+", key), cp.sections()):
            type_instance = self.__getInstance(MachineType, cp[machine_section]["type"])
            if type_instance is None:
                continue
            machine_instance = MachineInstance(cp[machine_section]["name"], type_instance)
            for setting in machine_instance:
                if setting.type.key in cp[machine_section]:
                    setting.value = cp[machine_section][setting.type.key]

            export = self.__getInstance(Export, cp[machine_section].get("export", ""))
            if export is None:
                continue
            machine_instance.export = export

            for tool_section in filter(lambda key: re.fullmatch("%s_tool_[0-9]+" % (machine_section), key), cp.sections()):
                type_instance = self.__getInstance(ToolType, cp[tool_section]["type"])
                if type_instance is None:
                    continue
                tool_instance = ToolInstance(machine_instance, type_instance)
                tool_instance.name = cp[tool_section]["name"]
                machine_instance.tools.append(tool_instance)
                for setting in tool_instance:
                    if setting.type.key in cp[tool_section]:
                        setting.value = cp[tool_section][setting.type.key]

                for operation_section in filter(lambda key: re.fullmatch("%s_operation_[0-9]+" % (tool_section), key), cp.sections()):
                    type_instance = self.__getInstance(JobOperationType, cp[operation_section]["type"])
                    if type_instance is None:
                        continue
                    operation_instance = JobOperationInstance(tool_instance, type_instance)
                    operation_instance.name = cp[operation_section]["name"]
                    for setting in operation_instance:
                        if setting.type.key in cp[operation_section]:
                            setting.value = cp[operation_section][setting.type.key]

                    tool_instance.operations.append(operation_instance)
            machines.append(machine_instance)
        return True

    @staticmethod
    def __getInstance(base_class: Type[T], class_name: str) -> Optional[T]:
        class_instance = PluginRegistry.getInstance().getClass(base_class, class_name)
        if class_instance is None:
            log.warning("Failed to find class: <%s> of type %s", class_name, base_class)
            return None
        return class_instance()

    def save(self, machines: QObjectList[MachineInstance]) -> None:
        cp = configparser.ConfigParser()
        for machine_index, machine in enumerate(machines):
            self._addSettingContainer(cp, "machine_%d" % (machine_index), machine)
            cp.set("machine_%d" % (machine_index), "export", type(machine.export).__name__)
            for tool_index, tool in enumerate(machine.tools):
                self._addSettingContainer(cp, "machine_%d_tool_%d" % (machine_index, tool_index), tool)
                for operation_index, operation in enumerate(tool.operations):
                    self._addSettingContainer(cp, "machine_%d_tool_%d_operation_%d" % (machine_index, tool_index, operation_index), operation)

        os.makedirs(os.path.dirname(self.__configuration_file), exist_ok=True)
        cp.write(open(self.__configuration_file, "wt"))

    @staticmethod
    def _addSettingContainer(cp: configparser.ConfigParser, section: str, setting_container: QObjectList[SettingInstance]) -> None:
        cp.add_section(section)
        cp.set(section, "name", setting_container.name)
        cp.set(section, "type", type(setting_container.type).__name__)
        for setting in setting_container:
            cp.set(section, setting.type.key, setting.value)
