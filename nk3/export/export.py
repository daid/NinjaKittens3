import logging
from typing import List

from PyQt5.QtCore import QUrl

import nk3.application
from nk3.processor.pathUtils import Move
from nk3.qt.QObjectBase import QObjectBase, QProperty, qtSlot

log = logging.getLogger(__name__.split(".")[-1])


class Export(QObjectBase):
    save_button_text = QProperty[str]("Save")
    qml_source = QProperty[str]("export/SaveGCode.qml")

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def getMoves() -> List[Move]:
        return nk3.application.Application.getInstance().move_data

    @qtSlot
    def save(self, filename: QUrl) -> None:
        log.info("Exporting to %s", filename.toLocalFile())
        f = open(filename.toLocalFile(), "wt")
        f.write(";NinjaKittens3 export!\n")
        for move in self.getMoves():
            f.write("G1 F%d X%f Y%f Z%f\n" % (move.speed, move.xy.real, move.xy.imag, move.z))
        f.close()
