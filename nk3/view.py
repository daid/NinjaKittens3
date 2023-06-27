import math
import numpy

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QAbstractOpenGLFunctions

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode

MYPY = False
if MYPY:
    from nk3.application import Application


class View:
    def __init__(self, application: "Application") -> None:
        self.__application = application
        self.__zoom = 30.0
        self.__yaw = 0.0
        self.__pitch = 0.0
        self.__view_position = complex(0, 0)
        self.__projection_matrix = None
        self.__model_matrix = None

    def render(self, gl: QAbstractOpenGLFunctions, size: QSize) -> None:
        gl.glViewport(0, 0, size.width(), size.height())
        gl.glUseProgram(0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_BLEND)
        gl.glClearColor(0.8, 0.8, 0.8, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        self.glPerspective(gl, 60.0, size, 1.0, self.__zoom * 4.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self._renderDocuments(gl)
        self.__projection_matrix = numpy.matrix(numpy.array(gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)).reshape((4, 4)))
        self.__model_matrix = numpy.matrix(numpy.array(gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)).reshape((4, 4)))
        self.__viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)

    def _renderDocuments(self, gl: QAbstractOpenGLFunctions) -> None:
        gl.glTranslatef(0, 0, -self.__zoom)
        gl.glRotatef(-self.__pitch, 1, 0, 0)
        gl.glRotatef(-self.__yaw, 0, 0, 1)
        gl.glTranslatef(-self.__view_position.real, -self.__view_position.imag, 0)

        gl.glLineWidth(3)
        gl.glBegin(gl.GL_LINES)
        gl.glColor4ub(0xFF, 0, 0, 0xFF)
        gl.glVertex3f(0, 0, 0)
        gl.glVertex3f(10, 0, 0)
        gl.glColor4ub(0, 0xFF, 0, 0xFF)
        gl.glVertex3f(0, 0, 0)
        gl.glVertex3f(0, 10, 0)
        gl.glColor4ub(0, 0, 0xFF, 0xFF)
        gl.glVertex3f(0, 0, 0)
        gl.glVertex3f(0, 0, 10)
        gl.glEnd()

        self._renderFrame(gl)

        for node in self.__application.document_list:
            self._renderDocument(gl, node)

        result_data = self.__application.result_data
        gl.glBegin(gl.GL_LINE_STRIP)
        for move in result_data.moves:
            if move.z < 0.0:
                gl.glColor4ub(0x00, 0x00, 0x00, 0xFF)
            else:
                gl.glColor4ub(0x80, 0x80, 0xFF, 0xFF)
            gl.glVertex3f(move.xy.real, move.xy.imag, move.z)
        gl.glEnd()

    def _renderFrame(self, gl: QAbstractOpenGLFunctions) -> None:
        aabb = self._getAABB()

        gl.glLineWidth(2)
        gl.glBegin(gl.GL_LINES)
        gl.glColor4ub(0x80, 0x80, 0x80, 0xFF)
        gl.glVertex3f(aabb[0].real, aabb[0].imag, 0)
        gl.glVertex3f(aabb[1].real, aabb[0].imag, 0)
        gl.glVertex3f(aabb[1].real, aabb[0].imag, 0)
        gl.glVertex3f(aabb[1].real, aabb[1].imag, 0)
        gl.glVertex3f(aabb[1].real, aabb[1].imag, 0)
        gl.glVertex3f(aabb[0].real, aabb[1].imag, 0)
        gl.glVertex3f(aabb[0].real, aabb[1].imag, 0)
        gl.glVertex3f(aabb[0].real, aabb[0].imag, 0)
        for x in range(int(aabb[0].real), int(aabb[1].real) + 10, 10):
            width = 2
            if x % 100 == 0:
                width = 7
            if x % 100 == 50:
                width = 4
            gl.glVertex3f(x, aabb[0].imag, 0)
            gl.glVertex3f(x, aabb[0].imag - width, 0)
        for y in range(int(aabb[0].imag), int(aabb[1].imag) + 10, 10):
            width = 2
            if y % 100 == 0:
                width = 7
            if y % 100 == 50:
                width = 4
            gl.glVertex3f(aabb[0].real, y, 0)
            gl.glVertex3f(aabb[0].real - width, y, 0)
        gl.glEnd()

    def _renderDocument(self, gl: QAbstractOpenGLFunctions, document: DocumentNode) -> None:
        if isinstance(document, DocumentVectorNode):
            color = document.color
            gl.glColor4ub(color & 0xFF, (color >> 8) & 0xFF, (color >> 16) & 0xFF, 0xFF)
            gl.glLineWidth(5)
            for path in document.getPaths():
                if path.closed:
                    gl.glBegin(gl.GL_LINE_LOOP)
                else:
                    gl.glBegin(gl.GL_LINE_STRIP)
                for point in path:
                    gl.glVertex3f(point.real, point.imag, 0)
                gl.glEnd()
            gl.glLineWidth(1)
        for node in document:
            self._renderDocument(gl, node)

    @property
    def pitch(self) -> float:
        return self.__pitch

    @pitch.setter
    def pitch(self, pitch: float) -> None:
        self.__pitch = min(max(0, pitch), 180)
        self.__application.repaint()

    @property
    def yaw(self) -> float:
        return self.__yaw

    @yaw.setter
    def yaw(self, yaw: float) -> None:
        self.__yaw = yaw
        self.__application.repaint()

    @property
    def zoom(self) -> float:
        return self.__zoom

    @zoom.setter
    def zoom(self, zoom: float) -> None:
        self.__zoom = max(zoom, 1.0)
        self.__application.repaint()

    @property
    def view_position(self) -> complex:
        return self.__view_position

    @view_position.setter
    def view_position(self, view_position: complex) -> None:
        self.__view_position = view_position
        self.__application.repaint()

    def screen_to_world(self, x, y):
        x = (x - self.__viewport[0]) / self.__viewport[2]
        y = (y - self.__viewport[1]) / self.__viewport[3]
        x = x * 2 - 1
        y = -(y * 2 - 1)
        m = numpy.linalg.inv(self.__projection_matrix.T)
        p = numpy.linalg.inv(self.__model_matrix.T)
        m = p * m
        v = numpy.array([x,x, y,y, 0,1, 1,1]).reshape((4,2))
        v = m * v
        v0 = (v[0:3,0] / v[3,0]).A.flatten()
        v1 = (v[0:3,1] / v[3,1]).A.flatten()
        d = v1 - v0
        d = d / numpy.linalg.norm(d)
        v = v0 + d / d[2] * -v0[2]
        return complex(v[0], v[1])

    def _getAABB(self):
        combined_aabb = None
        for document in self.__application.document_list:
            aabb = document.getAABB()
            if aabb is not None:
                if combined_aabb is None:
                    combined_aabb = aabb
                else:
                    combined_aabb = (
                        complex(min(combined_aabb[0].real, aabb[0].real), min(combined_aabb[0].imag, aabb[0].imag)),
                        complex(max(combined_aabb[1].real, aabb[1].real), max(combined_aabb[1].imag, aabb[1].imag)))
        return combined_aabb

    def home(self) -> None:
        combined_aabb = self._getAABB()
        if combined_aabb is not None:
            size = combined_aabb[1] - combined_aabb[0]
            zoom = max(size.real, size.imag) / 0.8
            self.view_position = (combined_aabb[0] + combined_aabb[1]) / 2.0
            self.zoom = zoom

    @staticmethod
    def glPerspective(gl: QAbstractOpenGLFunctions, fov: float, window_size: QSize, near: float, far: float) -> None:
        aspect = window_size.width() / window_size.height()
        y = math.tan(fov / 360 * math.pi) * near
        if aspect > 1.0:
            x = y * aspect
        else:
            x = y
            y = y / aspect
        gl.glFrustum(-x, x, -y, y, near, far)
