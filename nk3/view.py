import logging
import math

from nk3.depthFirstIterator import DepthFirstIterator
from nk3.document.vectorNode import DocumentVectorNode

log = logging.getLogger(__name__.split(".")[-1])

MYPY = False
if MYPY:
    from nk3.main import Application


class View:
    def __init__(self, application: "Application"):
        self.__application = application
        self.__zoom = 30
        self.__yaw = 0
        self.__pitch = 0
        self.__view_position = complex(0, 0)

    def render(self, gl, size):
        gl.glViewport(0, 0, size.width(), size.height())
        gl.glUseProgram(0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_BLEND)
        gl.glClearColor(0.8, 0.8, 0.8, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        self.glPerspective(gl, 90.0, size, 1.0, self.__zoom * 4.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self._renderDocuments(gl)

    def _renderDocuments(self, gl):
        gl.glTranslatef(0, 0, -self.__zoom)
        gl.glRotatef(-self.__pitch, 1, 0, 0)
        gl.glRotatef(-self.__yaw, 0, 0, 1)
        gl.glTranslatef(-self.__view_position.real, -self.__view_position.imag, 0)

        for node in self.__application.document_list:
            self._renderDocument(gl, node)

        move_data = self.__application.move_data
        if move_data is not None:
            gl.glColor4ub(0xFF, 0xFF, 0xFF, 0xFF)
            gl.glBegin(gl.GL_LINE_STRIP)
            for move in move_data:
                if move.xy is not None:
                    gl.glVertex3f(move.xy.real, move.xy.imag, move.z)
            gl.glEnd()

    def _renderDocument(self, gl, document):
        if isinstance(document, DocumentVectorNode):
            color = document.color
            gl.glColor4ub(color & 0xFF, (color >> 8) & 0xFF, (color >> 16) & 0xFF, 0xFF)
            for path in document.getPaths():
                if path.closed:
                    gl.glBegin(gl.GL_LINE_LOOP)
                else:
                    gl.glBegin(gl.GL_LINE_STRIP)
                for point in path:
                    gl.glVertex3f(point.real, point.imag, 0)
                gl.glEnd()
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
        self.__zoom = max(zoom, 1)
        self.__application.repaint()

    @property
    def view_position(self) -> complex:
        return self.__view_position

    @view_position.setter
    def view_position(self, view_position: complex) -> None:
        self.__view_position = view_position
        self.__application.repaint()

    def home(self):
        combined_aabb = None
        for document in DepthFirstIterator(self.__application.document_list):
            aabb = document.getAABB()
            if aabb is not None:
                if combined_aabb is None:
                    combined_aabb = aabb
                else:
                    combined_aabb = (
                        complex(min(combined_aabb[0].real, aabb[0].real), min(combined_aabb[0].imag, aabb[0].imag)),
                        complex(max(combined_aabb[1].real, aabb[1].real), max(combined_aabb[1].imag, aabb[1].imag)))
        if combined_aabb is not None:
            size = combined_aabb[1] - combined_aabb[0]
            zoom = max(size.real, size.imag) / 1.8
            self.view_position = (combined_aabb[0] + combined_aabb[1]) / 2.0
            self.zoom = zoom

    @staticmethod
    def glPerspective(gl, fov, window_size, near, far):
        aspect = window_size.width() / window_size.height()
        y = math.tan(fov / 360 * math.pi) * near
        if aspect > 1.0:
            x = y * aspect
        else:
            x = y
            y = y / aspect
        gl.glFrustum(-x, x, -y, y, near, far)
