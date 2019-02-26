from PyQt5.QtCore import pyqtProperty, QObject

from nk3.QObjectBase import QObjectBase, QObjectBaseProperty
from nk3.settingType import SettingType


class SettingInstance(QObjectBase):
    value = QObjectBaseProperty[str]("")

    def __init__(self, setting_type: SettingType):
        super().__init__()
        self.__type = setting_type
        self.value = setting_type.default_value

    @pyqtProperty(QObject, constant=True)
    def type(self):
        return self.__type
