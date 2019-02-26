import sys
import logging
import os

from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QGuiApplication, QOpenGLContext, QOpenGLVersionProfile
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType
from PyQt5.QtQuick import QQuickWindow, QQuickItem
from typing import List

from nk3.QObjectBase import qtSlot
from nk3.QObjectList import QObjectList
from nk3.machine.tool.toolInstance import ToolInstance
from nk3.machine.tool.cutToolType import CutToolType
from nk3.machine.operation.jobOperationInstance import JobOperationInstance

from nk3.fileReader.fileReader import FileReader
from nk3.processor.dispatcher import Dispatcher
from nk3.processor.export import Export
from nk3.processor.pathUtils import Move
from nk3.view import View
from nk3.configuration.storage import Storage

log = logging.getLogger(__name__.split(".")[-1])


class MainWindow(QQuickWindow):
    requestRepaint = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._gl = None
        self._gl_context = None

        self.setClearBeforeRendering(False)
        self.beforeRendering.connect(self._render, type=Qt.DirectConnection)
        self.requestRepaint.connect(self.update)

    def _initialize(self) -> None:
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        self._gl.initializeOpenGLFunctions()

    def _render(self) -> None:
        if self._gl is None:
            self._initialize()
        Application.getInstance().getView().render(self._gl, self.size())


class MouseHandler(QQuickItem):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.__last_pos = None

    def mousePressEvent(self, event) -> None:
        self.setFocus(True)  # Steal focus from whatever had it, so we unfocus text boxes.
        self.__last_pos = event.pos()

    def mouseReleaseEvent(self, event) -> None:
        pass

    def mouseMoveEvent(self, event) -> None:
        Application.getInstance().getView().yaw += (event.pos().x() - self.__last_pos.x())
        Application.getInstance().getView().pitch += (event.pos().y() - self.__last_pos.y())
        self.__last_pos = event.pos()

    def wheelEvent(self, event) -> None:
        Application.getInstance().getView().zoom *= 1.0 - (event.angleDelta().y() / 120.0) * 0.1


class Application(QObject):
    _instance = None

    @classmethod
    def getInstance(cls, *args) -> "Application":
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        assert Application._instance is None
        Application._instance = self
        
        self.__app = QGuiApplication(sys.argv)
        self.__qml_engine = QQmlApplicationEngine(self.__app)

        self.__view = View(self)

        qmlRegisterType(MainWindow, "NK3", 1, 0, "MainWindow")
        qmlRegisterType(MouseHandler, "NK3", 1, 0, "MouseHandler")
        qmlRegisterSingletonType(Application, "NK3", 1, 0, "Application", Application.getInstance)

        self.__move_data = None

        self.__cut_tool_list = QObjectList("tool")

        self.__document_list = QObjectList("node")
        self.__document_list.rowsInserted.connect(lambda parent, first, last: self.__view.home())

        self.__dispatcher = Dispatcher(self.__cut_tool_list, self.__document_list)
        self.__dispatcher.onMoveData = self.__onMoveData

        Storage().load(self.__cut_tool_list)
        if self.__cut_tool_list.size() == 0:
            self.createNewTool("Tool ?")

        self.__qml_engine.rootContext().setContextProperty("cut_tool_list", self.__cut_tool_list)
        self.__qml_engine.rootContext().setContextProperty("document_list", self.__document_list)
        self.__qml_engine.load(QUrl("resources/qml/Main.qml"))

        self.__app.aboutToQuit.connect(self._onQuit)

    @property
    def document_list(self) -> QObjectList:
        return self.__document_list

    @property
    def move_data(self) -> List[Move]:
        return self.__move_data

    def __onMoveData(self, move_data) -> None:
        self.__move_data = move_data
        self.repaint()

    def getView(self) -> View:
        return self.__view

    def repaint(self) -> None:
        self.__qml_engine.rootObjects()[0].requestRepaint.emit()

    def start(self) -> int:
        if not self.__qml_engine.rootObjects():
            return -1
        return self.__app.exec_()

    @qtSlot
    def reloadQML(self) -> None:
        for window in self.__qml_engine.rootObjects():
            window.close()
        self.__qml_engine.clearComponentCache()
        self.__qml_engine.load(QUrl("resources/qml/Main.qml"))

    @qtSlot
    def loadFile(self, filename: QUrl) -> None:
        try:
            log.info("Going to load: %s", filename.toLocalFile())
            reader = FileReader.getFileTypes()[os.path.splitext(filename.toLocalFile())[1][1:].lower()]
            document_node = reader().load(filename.toLocalFile())
        except Exception:
            log.exception("Load file failed for: %s", filename.toLocalFile())
        else:
            while len(self.__document_list) > 0:
                self.__document_list.remove(0)
            self.__document_list.append(document_node)
        self.repaint()

    @qtSlot
    def getLoadFileTypes(self) -> List[str]:
        types = FileReader.getFileTypes()
        result = ["Vector files (%s)" % (" ".join(["*.%s" % ext for ext in types.keys()]))]
        for ext in types.keys():
            result.append("%s (*.%s)" % (ext, ext))
        return result

    @qtSlot
    def exportFile(self, filename: QUrl) -> None:
        Export().export(filename.toLocalFile(), self.__move_data)

    @qtSlot
    def createNewTool(self, tool_name: str) -> None:
        instance = ToolInstance(tool_name, CutToolType())
        for operation_type in instance.type.getOperationTypes():
            instance.operations.append(JobOperationInstance(instance, operation_type))
        self.__cut_tool_list.append(instance)

    def _onQuit(self) -> None:
        Storage().save(self.__cut_tool_list)
