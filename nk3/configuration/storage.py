import logging
import configparser
import os
import re
import importlib
from typing import Any

from nk3.qt.QObjectList import QObjectList
from nk3.machine.machineInstance import MachineInstance
from nk3.machine.tool.toolInstance import ToolInstance
from nk3.machine.operation.jobOperationInstance import JobOperationInstance
from nk3.settingInstance import SettingInstance

log = logging.getLogger(__name__.split(".")[-1])


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
            type_instance = self.__getInstance(cp[machine_section]["type"])
            if type_instance is None:
                continue
            machine_instance = MachineInstance(cp[machine_section]["name"], type_instance)
            machines.append(machine_instance)
            for setting in machine_instance:
                if setting.type.key in cp[machine_section]:
                    setting.value = cp[machine_section][setting.type.key]

            for tool_section in filter(lambda key: re.fullmatch("%s_tool_[0-9]+" % (machine_section), key), cp.sections()):
                type_instance = self.__getInstance(cp[tool_section]["type"])
                if type_instance is None:
                    continue
                tool_instance = ToolInstance(machine_instance, type_instance)
                machine_instance.tools.append(tool_instance)
                for setting in tool_instance:
                    if setting.type.key in cp[tool_section]:
                        setting.value = cp[tool_section][setting.type.key]

                for operation_section in filter(lambda key: re.fullmatch("%s_operation_[0-9]+" % (tool_section), key), cp.sections()):
                    type_instance = self.__getInstance(cp[operation_section]["type"])
                    if type_instance is None:
                        continue
                    operation_instance = JobOperationInstance(tool_instance, type_instance)
                    operation_instance.name = cp[operation_section]["name"]
                    for setting in operation_instance:
                        if setting.type.key in cp[operation_section]:
                            setting.value = cp[operation_section][setting.type.key]

                    tool_instance.operations.append(operation_instance)
        return True

    @staticmethod
    def __getInstance(full_class_name: str) -> Any:
        module_name, _, class_name = full_class_name.rpartition(".")
        try:
            type_instance = getattr(importlib.import_module(module_name), class_name)()
        except ImportError:
            log.warning("Failed to find module: %s", module_name)
            return None
        except AttributeError:
            log.warning("Failed to find %s in module %s", class_name, module_name)
            return None
        return type_instance

    def save(self, machines: QObjectList[MachineInstance]) -> None:
        cp = configparser.ConfigParser()
        for machine_index, machine in enumerate(machines):
            self._addSettingContainer(cp, "machine_%d" % (machine_index), machine)
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
        cp.set(section, "type", "%s.%s" % (type(setting_container.type).__module__, type(setting_container.type).__name__))
        for setting in setting_container:
            cp.set(section, setting.type.key, setting.value)
