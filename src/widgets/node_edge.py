from PySide2.QtCore import QPointF, Qt, QRectF
from PySide2.QtGui import QPen, QPainterPath, QColor

from PySide2.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItem
)


class NodeEdgeGraphics(QGraphicsPathItem):
    def __init__(self, start_socket, end_socket):
        super().__init__(start_socket.socket_graphics)

        self.start_socket = start_socket
        self.end_socket = end_socket

        self._set_colors()
        self._set_flags()

    def _set_colors(self):
        self._pen_selected = QPen(QColor('#DD8600'))
        self._pen_selected.setWidthF(3.0)

        self._pen = QPen(QColor("#001000"))
        self._pen.setWidthF(3.0)

    def _set_flags(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # FIXME: edge stays on top of the socket
        self.setZValue(-1.0)

    def paint(self, painter, option, widget=None):
        path = QPainterPath(QPointF(0, 0))
        path.lineTo(self.mapFromScene(self.end_socket.get_position()))
        # self.setPath(path)

        painter.setPen(self._pen_selected if self.isSelected() else self._pen)
        painter.drawPath(path)
        # painter.drawPath(self.path())

    def boundingRect(self):
        return self.shape().boundingRect()


class NodeEdge:
    def __init__(self, start_socket, end_socket):

        self.edge_graphics = NodeEdgeGraphics(start_socket, end_socket)
