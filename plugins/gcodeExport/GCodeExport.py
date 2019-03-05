import logging

from PyQt5.QtCore import QUrl

from nk3.machine.export import Export
from nk3.qt.QObjectBase import qtSlot
from nk3.settingType import SettingType

log = logging.getLogger(__name__.split(".")[-1])


class GCodeExport(Export):
    def __init__(self) -> None:
        super().__init__([
            SettingType(key="start_code", label="Start GCode", type="gcode", default=""),
            SettingType(key="end_code", label="Start GCode", type="gcode", default=""),
        ])
        self.save_button_text = "Save"
        self.setLocalQmlSource("SaveGCode.qml")

    @qtSlot
    def save(self, filename: QUrl) -> None:
        log.info("Exporting to %s", filename.toLocalFile())
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
