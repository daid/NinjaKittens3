import configparser
import logging
import os
import re
from typing import Type, TypeVar, Optional

from nk3.machine.machine import Machine
from nk3.machine.operation import Operation
from nk3.machine.tool import Tool
from nk3.machine.outputmethod import OutputMethod
from nk3.pluginRegistry import PluginRegistry
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance

T = TypeVar("T", bound=QObjectList[SettingInstance])


class Storage:
    def __init__(self) -> None:
        config_base_path = os.environ.get("APPDATA", None)
        if config_base_path is None:
            config_base_path = os.path.expanduser("~/.config")
        self.__configuration_file = os.path.join(config_base_path, "NinjaKittens3", "nk3.conf")
        self.__cp = configparser.ConfigParser()

    def load(self) -> bool:
        if not self.__cp.read(self.__configuration_file):
            return False
        return True

    def loadMachines(self, machines: QObjectList[Machine]) -> bool:
        for machine_section in filter(lambda key: re.fullmatch("machine_[0-9]+", key), self.__cp.sections()):
            machine_instance = self.__createInstanceFromSettings(Machine, self.__cp[machine_section])
            if machine_instance is None:
                continue

            output_method_section = "%s_output_method" % (machine_section)
            if output_method_section not in self.__cp:
                continue
            output_method = self.__createInstanceFromSettings(OutputMethod, self.__cp[output_method_section])
            if output_method is None:
                continue
            machine_instance.output_method = output_method

            for tool_section in filter(lambda key: re.fullmatch("%s_tool_[0-9]+" % (machine_section), key), self.__cp.sections()):
                tool_instance = self.__createInstanceFromSettings(Tool, self.__cp[tool_section])
                if tool_instance is None:
                    continue
                machine_instance.tools.append(tool_instance)

                for operation_section in filter(lambda key: re.fullmatch("%s_operation_[0-9]+" % (tool_section), key), self.__cp.sections()):
                    operation_instance = self.__createInstanceFromSettings(Operation, self.__cp[operation_section])
                    if operation_instance is None:
                        continue
                    tool_instance.operations.append(operation_instance)
            machines.append(machine_instance)
        return True

    @staticmethod
    def __createInstanceFromSettings(base_class: Type[T], section: configparser.SectionProxy) -> Optional[T]:
        instance = Storage.__getInstance(base_class, section.get("type", fallback="UNSET"))
        if instance is None:
            return None
        if hasattr(instance, "name"):
            instance.name = section.get("name", fallback=instance.name)
        for setting in instance:
            if setting.type.key in section:
                setting.value = section[setting.type.key]
        return instance

    @staticmethod
    def __getInstance(base_class: Type[T], class_name: str) -> Optional[T]:
        class_instance = PluginRegistry.getInstance().getClass(base_class, class_name)
        if class_instance is None:
            logging.warning("Failed to find class: <%s> of type %s", class_name, base_class)
            return None
        return class_instance()  # type: ignore

    def storeMachines(self, machines: QObjectList[Machine]) -> None:
        for machine_index, machine in enumerate(machines):
            self.__addSettingContainer(self.__cp, "machine_%d" % (machine_index), machine)
            self.__addSettingContainer(self.__cp, "machine_%d_output_method" % (machine_index), machine.output_method)
            for tool_index, tool in enumerate(machine.tools):
                self.__addSettingContainer(self.__cp, "machine_%d_tool_%d" % (machine_index, tool_index), tool)
                for operation_index, operation in enumerate(tool.operations):
                    self.__addSettingContainer(self.__cp, "machine_%d_tool_%d_operation_%d" % (machine_index, tool_index, operation_index), operation)

        os.makedirs(os.path.dirname(self.__configuration_file), exist_ok=True)

    def save(self) -> None:
        self.__cp.write(open(self.__configuration_file, "wt"))

    @staticmethod
    def __addSettingContainer(cp: configparser.ConfigParser, section: str, setting_container: QObjectList[SettingInstance]) -> None:
        cp.add_section(section)
        if hasattr(setting_container, "name"):
            cp.set(section, "name", setting_container.name)
        cp.set(section, "type", type(setting_container).__name__)
        for setting in setting_container:
            cp.set(section, setting.type.key, setting.value)

    def getGeneralSetting(self, key: str) -> str:
        return self.__cp.get("general", key, fallback="")

    def setGeneralSetting(self, key: str, value: str) -> None:
        if not self.__cp.has_section("general"):
            self.__cp.add_section("general")
        self.__cp.set("general", key, value)
