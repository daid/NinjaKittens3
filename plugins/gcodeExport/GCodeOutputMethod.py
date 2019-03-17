import logging

from PyQt5.QtCore import QUrl

from nk3.machine.outputmethod import OutputMethod
from nk3.qt.QObjectBase import qtSlot
from nk3.settingType import SettingType


class GCodeOutputMethod(OutputMethod):
    NAME = "GCode Export"

    def __init__(self) -> None:
        super().__init__([
            SettingType(key="start_code", label="Start GCode", type="gcode", default="",
                        tooltip="""GCode that is inserted before the actual instructions to
                        generate the object. Things to prepare the machine can be put here,
                        like spinning up your spindle, setting coordinate systems."""),
            SettingType(key="end_code", label="End GCode", type="gcode", default="",
                        tooltip="""GCode that is inserted at the end of the instructions.
                        You can place code here to wind or disable your machine.
                        For example disabling motors, spindles."""),
        ])
        self.setLocalQmlSource("SaveGCode.qml")

    @qtSlot
    def save(self, filename: QUrl) -> None:
        logging.info("Exporting to %s", filename.toLocalFile())
        f = open(filename.toLocalFile(), "wt")
        start_code = self.getSettingValue("start_code").strip()
        if start_code != "":
            f.write(start_code + "\n")
        for move in self.getMoves():
            f.write("G1 F%d X%f Y%f Z%f\n" % (move.speed, move.xy.real, move.xy.imag, move.z))
        end_code = self.getSettingValue("end_code").strip()
        if end_code != "":
            f.write(end_code + "\n")
        f.close()
