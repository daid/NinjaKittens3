from PyQt5.QtCore import QObject, pyqtProperty


class SettingType(QObject):
    def __init__(self, key, label, type, default):
        super().__init__()
        self.__key = key
        self.__label = label
        self.__type = type
        self.__default_value = default

    @pyqtProperty(str, constant=True)
    def key(self):
        return self.__key

    @pyqtProperty(str, constant=True)
    def label(self):
        return self.__label

    @pyqtProperty(str, constant=True)
    def type(self):
        return self.__type

    @pyqtProperty(str, constant=True)
    def default_value(self):
        return self.__default_value

    @pyqtProperty(str, constant=True)
    def unit(self):
        if self.__type == "dimension":
            return "mm"
        if self.__type == "speed":
            return "mm/min"
        if self.__type == "percentage":
            return "%"
        return ""
