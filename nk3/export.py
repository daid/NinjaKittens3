import logging
import os
import sys
from typing import List

from PyQt5.QtCore import QUrl

import nk3.application
from nk3.processor.pathUtils import Move
from nk3.qt.QObjectBase import QObjectBase, QProperty, qtSlot

log = logging.getLogger(__name__.split(".")[-1])


class Export(QObjectBase):
    save_button_text = QProperty[str]("?")
    qml_source = QProperty[str]("")

    @staticmethod
    def getMoves() -> List[Move]:
        return nk3.application.Application.getInstance().move_data

    def setLocalQmlSource(self, filename: str) -> None:
        path = os.path.dirname(sys.modules[type(self).__module__].__file__)
        self.qml_source = "file://%s/%s" % (path, filename)
