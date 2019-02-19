import logging

from typing import Iterator, TYPE_CHECKING

from nk3.QObjectBase import QObjectBase
from nk3.QObjectList import QObjectList
from nk3.jobOperations.cutCenter import CutCenterOperation
from nk3.jobOperations.cutInside import CutInsideOperation
from nk3.jobOperations.cutOutside import CutOutsideOperation
from nk3.jobOperations.cutOutsideWithPocket import CutOutsideWithPocketOperation
from nk3.jobOperations.cutPocket import CutPocketOperation
from nk3.processor.settings import Settings
from nk3.settingType import SettingType
if TYPE_CHECKING:
    from nk3.cutToolInstance import CutToolInstance

log = logging.getLogger(__name__.split(".")[-1])


## The CutTool defines which settings are available for cutting tools
class CutToolType(QObjectBase):
    def __init__(self) -> None:
        super().__init__()
        self.__settings = [
            SettingType(key="tool_diameter", label="Endmill diameter", type="dimension", default="6.0"),
            SettingType(key="cut_depth_pass", label="Cut depth per pass", type="dimension", default="1.0"),
            SettingType(key="cut_feedrate", label="Feedrate", type="speed", default="1200"),
            SettingType(key="plunge_feedrate", label="Plungerate", type="speed", default="180"),
        ]
        self.__operations = QObjectList("operation")
        self.__operations.append(CutOutsideOperation())
        self.__operations.append(CutOutsideWithPocketOperation())
        self.__operations.append(CutInsideOperation())
        self.__operations.append(CutPocketOperation())
        self.__operations.append(CutCenterOperation())

    def getSettingTypes(self) -> Iterator[SettingType]:
        return iter(self.__settings)

    def getOperationTypes(self) -> QObjectList:
        return self.__operations

    def fillProcessorSettings(self, instance: "CutToolInstance", settings: Settings) -> None:
        settings.tool_diameter = float(instance.getSettingValue("tool_diameter"))
        settings.cut_depth_pass = float(instance.getSettingValue("cut_depth_pass"))
        settings.cut_feedrate = float(instance.getSettingValue("cut_feedrate"))
        settings.plunge_feedrate = float(instance.getSettingValue("plunge_feedrate"))
