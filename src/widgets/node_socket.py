
from PySide2.QtCore import Qt
from PySide2.QtGui import QPen, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsItem
)


class SocketGraphics(QGraphicsItem):
    def __init__(self, node, parent=None):
        super().__init__(node)

        self._outline_pen = QPen(Qt.black)
        self._outline_pen.setWidthF(0.5)

        self._draw_graphics()

    def _draw_graphics(self):
        """Draw the graphics of the socket ellipse."""
        path = QPainterPath()
        radius = 6.0
        path.addEllipse(-radius, -radius, radius * 2, radius * 2)
        self._socket_body = path

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(Qt.green))
        painter.setPen(self._outline_pen)
        painter.drawPath(self._socket_body)

    def boundingRect(self):
        return self._socket_body.boundingRect()

    def __str__(self) -> str:
        return f"<Socket {hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"


class Socket:
    def __init__(self, node=None):
        self.socket_graphics = SocketGraphics(node)
