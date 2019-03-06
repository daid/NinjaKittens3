import configparser
import logging
import os
import re
from typing import Type, TypeVar, Optional

from nk3.machine.machine import Machine
from nk3.machine.operation import Operation
from nk3.machine.tool import Tool
from nk3.machine.export import Export
from nk3.pluginRegistry import PluginRegistry
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance

log = logging.getLogger(__name__.split(".")[-1])

T = TypeVar("T", bound=QObjectList[SettingInstance])


class Storage:
    def __init__(self) -> None:
        config_base_path = os.environ.get("APPDATA", None)
        if config_base_path is None:
            config_base_path = os.path.expanduser("~/.config")
        self.__configuration_file = os.path.join(config_base_path, "NinjaKittens3", "nk3.conf")

    def load(self, machines: QObjectList[Machine]) -> bool:
        cp = configparser.ConfigParser()
        if not cp.read(self.__configuration_file):
            return False
        for machine_section in filter(lambda key: re.fullmatch("machine_[0-9]+", key), cp.sections()):
            machine_instance = self.__createInstanceFromSettings(Machine, cp[machine_section])
            if machine_instance is None:
                continue

            export_section = "%s_export" % (machine_section)
            export = self.__createInstanceFromSettings(Export, cp[export_section])
            if export is None:
                continue
            machine_instance.export = export

            for tool_section in filter(lambda key: re.fullmatch("%s_tool_[0-9]+" % (machine_section), key), cp.sections()):
                tool_instance = self.__createInstanceFromSettings(Tool, cp[tool_section])
                if tool_instance is None:
                    continue
                machine_instance.tools.append(tool_instance)

                for operation_section in filter(lambda key: re.fullmatch("%s_operation_[0-9]+" % (tool_section), key), cp.sections()):
                    operation_instance = self.__createInstanceFromSettings(Operation, cp[operation_section])
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
            log.warning("Failed to find class: <%s> of type %s", class_name, base_class)
            return None
        return class_instance()  # type: ignore

    def save(self, machines: QObjectList[Machine]) -> None:
        cp = configparser.ConfigParser()
        for machine_index, machine in enumerate(machines):
            self.__addSettingContainer(cp, "machine_%d" % (machine_index), machine)
            self.__addSettingContainer(cp, "machine_%d_export" % (machine_index), machine.export)
            for tool_index, tool in enumerate(machine.tools):
                self.__addSettingContainer(cp, "machine_%d_tool_%d" % (machine_index, tool_index), tool)
                for operation_index, operation in enumerate(tool.operations):
                    self.__addSettingContainer(cp, "machine_%d_tool_%d_operation_%d" % (machine_index, tool_index, operation_index), operation)

        os.makedirs(os.path.dirname(self.__configuration_file), exist_ok=True)
        cp.write(open(self.__configuration_file, "wt"))

    @staticmethod
    def __addSettingContainer(cp: configparser.ConfigParser, section: str, setting_container: QObjectList[SettingInstance]) -> None:
        cp.add_section(section)
        if hasattr(setting_container, "name"):
            cp.set(section, "name", setting_container.name)
        cp.set(section, "type", type(setting_container).__name__)
        for setting in setting_container:
            cp.set(section, setting.type.key, setting.value)
