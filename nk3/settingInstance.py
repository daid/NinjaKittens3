from PyQt5.QtCore import pyqtProperty, QObject

from nk3.qt.QObjectBase import QObjectBase, QProperty
from nk3.settingType import SettingType


class SettingInstance(QObjectBase):
    value = QProperty[str]("")

    def __init__(self, setting_type: SettingType) -> None:
        super().__init__()
        self.__type = setting_type
        self.value = setting_type.default_value

    @pyqtProperty(QObject, constant=True)
    def type(self) -> QObject:
        return self.__type
