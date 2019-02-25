import logging
import configparser
import os
import re
import importlib

from nk3.QObjectList import QObjectList
from nk3.toolInstance import ToolInstance
from nk3.jobOperationInstance import JobOperationInstance

log = logging.getLogger(__name__.split(".")[-1])

class Storage:
    def __init__(self) -> None:
        config_base_path = os.environ.get("APPDATA", None)
        if config_base_path is None:
            config_base_path = os.path.expanduser("~/.config")
        self.__configuration_file = os.path.join(config_base_path, "NinjaKittens3", "nk3.conf")

    def load(self, tools: QObjectList) -> bool:
        cp = configparser.ConfigParser()
        if not cp.read(self.__configuration_file):
            return False
        for section in filter(lambda key: re.fullmatch("tool_[0-9]+", key), cp.sections()):
            module_name, _, class_name = cp[section]["type"].rpartition(".")
            type_instance = getattr(importlib.import_module(module_name), class_name)()
            tool_instance = ToolInstance(cp[section]["name"], type_instance)
            for setting in tool_instance:
                if setting.type.key in cp[section]:
                    setting.value = cp[section][setting.type.key]
            
            for sub_section in filter(lambda key: re.fullmatch("%s_operation_[0-9]+" % (section), key), cp.sections()):
                module_name, _, class_name = cp[sub_section]["type"].rpartition(".")
                type_instance = getattr(importlib.import_module(module_name), class_name)()
                operation_instance = JobOperationInstance(tool_instance, type_instance)
                operation_instance.name = cp[sub_section]["name"]
                for setting in operation_instance:
                    if setting.type.key in cp[sub_section]:
                        setting.value = cp[sub_section][setting.type.key]

                tool_instance.operations.append(operation_instance)
            tools.append(tool_instance)
        return True

    def save(self, tools: QObjectList) -> None:
        cp = configparser.ConfigParser()
        for tool_index, tool in enumerate(tools):
            assert isinstance(tool, ToolInstance)
            self._addSettingContainer(cp, "tool_%d" % (tool_index), tool)
            for operation_index, operation in enumerate(tool.operations):
                self._addSettingContainer(cp, "tool_%d_operation_%d" % (tool_index, operation_index), operation)

        os.makedirs(os.path.dirname(self.__configuration_file), exist_ok=True)
        cp.write(open(self.__configuration_file, "wt"))

    @staticmethod
    def _addSettingContainer(cp: configparser.ConfigParser, section: str, setting_container) -> None:
        cp.add_section(section)
        cp.set(section, "name", setting_container.name)
        cp.set(section, "type", "%s.%s" % (type(setting_container.type).__module__, type(setting_container.type).__name__))
        for setting in setting_container:
            cp.set(section, setting.type.key, setting.value)
