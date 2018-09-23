import sys
import logging

from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QOpenGLContext, QOpenGLVersionProfile, QMouseEvent
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtQuick import QQuickWindow, QQuickItem

from nk3.QObjectList import QObjectList
from nk3.cutToolInstance import CutToolInstance
from nk3.cutToolType import CutToolType

from nk3.fileReader.dxf.dxfFileReader import DXFFileReader
from nk3.processor.dispatcher import Dispatcher
from nk3.view import View


class MainWindow(QQuickWindow):
    requestRepaint = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._gl = None
        self._gl_context = None

        self.setClearBeforeRendering(False)
        self.beforeRendering.connect(self._render, type=Qt.DirectConnection)
        self.requestRepaint.connect(self.update)

    def _initialize(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        self._gl.initializeOpenGLFunctions()

    def _render(self):
        if self._gl is None:
            self._initialize()
        Application.getInstance().getView().render(self._gl, self.size())

class MouseHandler(QQuickItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.__last_pos = None

    def mousePressEvent(self, event):
        self.setFocus(True)  # Steal focus from whatever had it, so we unfocus text boxes.
        self.__last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        Application.getInstance().getView().yaw += (event.pos().x() - self.__last_pos.x())
        Application.getInstance().getView().pitch += (event.pos().y() - self.__last_pos.y())
        self.__last_pos = event.pos()

    def wheelEvent(self, event):
        Application.getInstance().getView().zoom *= 1.0 - (event.angleDelta().y() / 120.0) * 0.1


class Application:
    _instance = None

    @classmethod
    def getInstance(cls) -> "Application":
        return Application._instance

    def __init__(self):
        assert Application._instance is None
        Application._instance = self

        self.__app = QGuiApplication(sys.argv)
        self.__qml_engine = QQmlApplicationEngine(self.__app)

        self.__view = View(self)

        qmlRegisterType(MainWindow, "NK3", 1, 0, "MainWindow")
        qmlRegisterType(MouseHandler, "NK3", 1, 0, "MouseHandler")

        self.__move_data = None

        self.__cut_tool_list = QObjectList()

        self.__document_list = QObjectList()
        self.__document_list.rowsInserted.connect(lambda parent, first, last: self.__view.home())

        self.__dispatcher = Dispatcher(self.__cut_tool_list, self.__document_list)
        self.__dispatcher.onMoveData = self.__onMoveData

        self.__cut_tool_list.append(CutToolInstance("3mm", CutToolType()))
        self.__cut_tool_list.append(CutToolInstance("8mm", CutToolType()))

        self.__qml_engine.rootContext().setContextProperty("cut_tool_list", self.__cut_tool_list)
        self.__qml_engine.rootContext().setContextProperty("document_list", self.__document_list)
        self.__qml_engine.load(QUrl("resources/qml/Main.qml"))

        # self.__document_list.append(DXFFileReader().load("C:/Models/CNC/RiderCNC/TableBeltTensioner.stl.dxf"))
        # self.__document_list.append(DXFFileReader().load("C:/Models/ForCNC/CarWheel.dxf"))
        self.__document_list.append(DXFFileReader().load("C:/Models/ForCNC/RoundedGearBoard.dxf"))
        # self.__document_list.append(DXFFileReader().load("test.dxf"))
        # self.__document_list[0].operation_index = 0
        # self.__document_list.append(DXFFileReader().load("C:/Software/NinjaKittens2/ch side top.dxf"))
        # self.__document_list.append(DXFFileReader().load("C:/Software/NinjaKittens2/1235-B2P-D1 3.dxf"))
        # import glob
        # for filename in glob.glob("_sample-files-master/dxf/**/*.dxf"):
        #     self.__document_list.append(DXFFileReader().load(filename))
        # self.__document_list.append(DXFFileReader().load("_sample-files-master/dxf/autocad2017/2Dhatch.dxf"))

    @property
    def document_list(self):
        return self.__document_list

    @property
    def move_data(self):
        return self.__move_data

    def __onMoveData(self, move_data):
        self.__move_data = move_data
        self.repaint()

    def getView(self):
        return self.__view

    def repaint(self):
        self.__qml_engine.rootObjects()[0].requestRepaint.emit()

    def start(self):
        if not self.__qml_engine.rootObjects():
            return -1
        return self.__app.exec_()


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s:%(levelname)10s:%(name)20s:%(message)s", level=logging.INFO)
    Application().start()
