import logging
import os
import sys
import math
from typing import List, Optional, Any

from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QGuiApplication, QOpenGLContext, QOpenGLVersionProfile, QAbstractOpenGLFunctions, QMouseEvent, \
    QWheelEvent, QHoverEvent
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, QQmlError
from PyQt5.QtQuick import QQuickWindow, QQuickItem

from nk3.configuration.storage import Storage
from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.fileReader.fileReader import FileReader
from nk3.machine.machine import Machine
from nk3.machine.outputmethod import OutputMethod
from nk3.pluginRegistry import PluginRegistry
from nk3.processor.dispatcher import Dispatcher
from nk3.processor.result import Result
from nk3.qt.QObjectBase import qtSlot, QObjectBase, QProperty
from nk3.qt.QObjectList import QObjectList
from nk3.view import View


class MainWindow(QQuickWindow):
    requestRepaint = pyqtSignal()

    def __init__(self, parent: QObject=None) -> None:
        super().__init__(parent)

        self._gl = None  # type: Optional[QAbstractOpenGLFunctions]
        self._gl_context = None

        self.setClearBeforeRendering(False)
        self.beforeRendering.connect(self._render, type=Qt.DirectConnection)
        self.requestRepaint.connect(self.update)
        self.setVisibility(QQuickWindow.Maximized)

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
    rightClick = pyqtSignal(QPoint)

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setAcceptHoverEvents(True)
        self.__last_pos = None  # type: Optional[QPoint]
        self.__done_drag = False

    def hoverMoveEvent(self, event: QHoverEvent) -> None:
        pass

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.setFocus(True)  # Steal focus from whatever had it, so we unfocus text boxes.
        self.__last_pos = event.pos()
        self.__done_drag = False

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.RightButton and not self.__done_drag:
            pos = Application.getInstance().getView().screen_to_world(event.pos().x(), event.pos().y())
            self.rightClick.emit(QPoint(pos.real, pos.imag))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.__done_drag = True
        if self.__last_pos is not None:
            view = Application.getInstance().getView()
            delta_x = (event.pos().x() - self.__last_pos.x()) / self.size().height()
            delta_y = (event.pos().y() - self.__last_pos.y()) / self.size().height()
            if event.buttons() & Qt.RightButton:
                prev = Application.getInstance().getView().screen_to_world(self.__last_pos.x(), self.__last_pos.y())
                current = Application.getInstance().getView().screen_to_world(event.pos().x(), event.pos().y())
                delta = prev - current
                view.view_position = view.view_position + delta
            else:
                view.yaw += delta_x * 360.0
                view.pitch += delta_y * 360.0
        self.__last_pos = event.pos()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        pos = Application.getInstance().getView().screen_to_world(event.pos().x(), event.pos().y())
        #Application.getInstance().active_machine.output_method.onDrawingDoubleClick(pos)

    def wheelEvent(self, event: QWheelEvent) -> None:
        Application.getInstance().getView().zoom *= 1.0 - (event.angleDelta().y() / 120.0) * 0.1


class Application(QObjectBase):
    _instance = None  # type: Optional["Application"]

    machine_list = QProperty[QObjectList[Machine]](QObjectList[Machine]("PLACEHOLDER"))
    active_machine = QProperty[Machine](Machine())
    result_info = QProperty[str]("No file loaded")
    highlight_node = QProperty[DocumentNode](None)

    @classmethod
    def getInstance(cls, *args: Any) -> "Application":
        assert cls._instance is not None
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        assert Application._instance is None
        Application._instance = self

        PluginRegistry.getInstance().findPlugins(os.path.join(os.getcwd(), "plugins"))

        self.__app = QGuiApplication(sys.argv)
        self.__app.setOrganizationName("daid")
        self.__app.setOrganizationDomain("daid.eu")
        self.__qml_engine = QQmlApplicationEngine(self.__app)
        self.__qml_engine.warnings.connect(self.__onWarning)
        self.__qml_engine.setOutputWarningsToStandardError(False)

        self.__view = View(self)

        qmlRegisterType(MainWindow, "NK3", 1, 0, "MainWindow")
        qmlRegisterType(MouseHandler, "NK3", 1, 0, "MouseHandler")
        qmlRegisterSingletonType(Application, "NK3", 1, 0, "Application", Application.getInstance)

        self.__process_result = Result()

        self.machine_list = QObjectList[Machine]("machine")

        self.__document_list = QObjectList[DocumentNode]("node")
        self.__document_list.rowsInserted.connect(lambda parent, first, last: self.__view.home())

        self.__dispatcher = Dispatcher(self.__document_list)
        self.__dispatcher.onResultData = self.__onResultData
        self.active_machineChanged.connect(self.__onActiveMachineChanged)
        self.highlight_nodeChanged.connect(self.__onHighlightChanged)

        self.__last_file = ""

        s = Storage()
        if s.load():
            s.loadMachines(self.machine_list)
            self.__last_file = s.getGeneralSetting("last_file")
            if os.path.isfile(self.__last_file):
                self._loadFile(self.__last_file)
        if self.machine_list.size() == 0:
            machine_type = PluginRegistry.getInstance().getClass(Machine, "RouterMachine")
            assert machine_type is not None
            self.machine_list.append(machine_type())
            output_method_type = PluginRegistry.getInstance().getClass(OutputMethod, "GCodeOutputMethod")
            if output_method_type is not None:
                self.machine_list[0].output_method = output_method_type()
            self.machine_list[0].addTool(self.machine_list[0].tool_types[0])
        self.active_machine = self.machine_list[0]

        self.__qml_engine.rootContext().setContextProperty("document_list", self.__document_list)
        self.__qml_engine.load(QUrl("resources/qml/Main.qml"))

        self.__app.aboutToQuit.connect(self._onQuit)

    def __onWarning(self, warnings: List[QQmlError]) -> None:
        for warning in warnings:
            logging.info("%s:%d %s", warning.url().toLocalFile(), warning.line(), warning.description())

    @property
    def document_list(self) -> QObjectList[DocumentNode]:
        return self.__document_list

    @property
    def result_data(self) -> Result:
        return self.__process_result

    def __onActiveMachineChanged(self) -> None:
        for node in DepthFirstIterator(self.__document_list):
            node.tool_index = -1
            node.operation_index = -1
        for machine in self.machine_list:
            if machine != self.active_machine:
                machine.output_method.release()
        self.__dispatcher.setActiveMachine(self.active_machine)
        self.active_machine.output_method.activate()
        self.__qml_engine.rootContext().setContextProperty("output_method", self.active_machine.output_method)

    def __onHighlightChanged(self) -> None:
        self.getView().highlight_node = self.highlight_node
        self.repaint()

    def __onResultData(self, result: Result) -> None:
        self.__process_result = result
        self.result_info = result.info()
        self.repaint()

    def getView(self) -> View:
        return self.__view

    def repaint(self) -> None:
        root_objects = self.__qml_engine.rootObjects()
        if len(root_objects) > 0:
            root_objects[0].requestRepaint.emit()

    def start(self) -> int:
        if not self.__qml_engine.rootObjects():
            return -1
        return self.__app.exec_()

    @qtSlot
    def reloadQML(self) -> None:
        for window in self.__qml_engine.rootObjects():
            window.close()
        self.__qml_engine.clearComponentCache()
        logging.info("Reloading QML")
        self.__qml_engine.load(QUrl("resources/qml/Main.qml"))

    @qtSlot
    def loadFile(self, filename: QUrl) -> None:
        self._loadFile(filename.toLocalFile())

    @qtSlot
    def home(self) -> None:
        self.__view.home()

    def _loadFile(self, filename: str) -> None:
        logging.info("Going to load: %s", filename)
        reader = FileReader.getFileTypes()[os.path.splitext(filename)[1][1:].lower()]
        document_node = reader().load(filename)
        while len(self.__document_list) > 0:
            self.__document_list.remove(0)
        self.__document_list.append(document_node)
        self.__last_file = filename
        self.repaint()

    @qtSlot
    def getLoadFileTypes(self) -> List[str]:
        types = FileReader.getFileTypes()
        result = ["Vector files (%s)" % (" ".join(["*.%s" % ext for ext in types.keys()]))]
        for ext in types.keys():
            result.append("%s (*.%s)" % (ext, ext))
        return result

    def _onQuit(self) -> None:
        s = Storage()
        s.setGeneralSetting("last_file", self.__last_file)
        s.storeMachines(self.machine_list)
        s.save()
