import logging

from PySide2.QtCore import QPointF
from PySide2.QtGui import QPen, QPainterPath, QColor

from PySide2.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItem,
    QGraphicsView
)

from src.utils import class_id

LOGGER = logging.getLogger('nodeeditor.edge')
LOGGER.setLevel(logging.DEBUG)


class NodeEdgeGraphics(QGraphicsPathItem):

    def __init__(self, view, start_socket, end_socket):
        super().__init__(start_socket)
        LOGGER.info('Creating edge')

        self.view: QGraphicsView = view
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.mouse_pos = (start_socket.get_position().x(),
                          start_socket.get_position().y())

        self._set_colors()
        self._set_flags()

        self.view.mouse_position.connect(self._set_mouse)

    def _set_colors(self):
        self._pen_selected = QPen(QColor('#DD8600'))
        self._pen_selected.setWidthF(3.0)

        self._pen = QPen(QColor("#001000"))
        self._pen.setWidthF(3.0)

    def _set_flags(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # FIXME: edge stays on top of the socket
        self.setZValue(-1.0)

    def _set_mouse(self, x, y):
        # FIXME: ugly
        self.mouse_pos = (x, y)

    def paint(self, painter, option, widget=None):
        path = QPainterPath(QPointF(0, 0))

        if self.end_socket:
            end = self.mapFromScene(self.end_socket.get_position())
        else:
            end = self.mapFromScene(*self.mouse_pos)

        path.lineTo(end)
        self.setPath(path)

        painter.setPen(self._pen_selected if self.isSelected() else self._pen)
        painter.drawPath(self.path())

    def boundingRect(self):
        return self.shape().boundingRect()

    def __str__(self) -> str:
        return class_id('NodeEdge', self)


class NodeEdge:
    def __init__(self, view, start_socket, end_socket):

        self.edge_graphics = NodeEdgeGraphics(view, start_socket, end_socket)
