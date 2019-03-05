import logging

from PyQt5.QtCore import QUrl

from nk3.machine.export import Export
from nk3.qt.QObjectBase import qtSlot

log = logging.getLogger(__name__.split(".")[-1])


class GCodeExport(Export):
    def __init__(self) -> None:
        super().__init__([])
        self.save_button_text = "Save"
        self.setLocalQmlSource("SaveGCode.qml")

    @qtSlot
    def save(self, filename: QUrl) -> None:
        log.info("Exporting to %s", filename.toLocalFile())
        f = open(filename.toLocalFile(), "wt")
        f.write(";NinjaKittens3 export!\n")
        for move in self.getMoves():
            f.write("G1 F%d X%f Y%f Z%f\n" % (move.speed, move.xy.real, move.xy.imag, move.z))
        f.close()
