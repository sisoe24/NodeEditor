import logging

from PySide2.QtCore import QPointF,  Qt
from PySide2.QtGui import QPen, QPainterPath, QColor, QPainterPathStroker

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
        LOGGER.debug('Creating edge')

        self.end_socket = end_socket

        self._mouse_position = self.mapToScene(QPointF(0, 0))
        view.mouse_position.connect(self._set_mouse)

        self._set_colors()
        self._set_flags()

    def _set_colors(self):
        self._pen_selected = QPen(QColor('#DD8600'))
        self._pen_selected.setWidthF(2.0)

        self._pen = QPen(QColor("#001000"))
        self._pen.setWidthF(2.0)

    def _set_flags(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent)

    def _set_mouse(self, x, y):
        # FIXME: ugly
        self._mouse_position = QPointF(x, y)

    def paint(self, painter, option, widget=None):
        stroke = QPainterPathStroker()
        stroke.setJoinStyle(Qt.RoundJoin)
        stroke.setWidth(1.5)

        path = QPainterPath(QPointF(0, 0))

        if self.end_socket:
            end = self.mapFromScene(self.end_socket.get_position())
        else:
            end = self.mapFromScene(self._mouse_position)

        path.lineTo(end)
        stroker_path = stroke.createStroke(path)

        self.setPath(stroker_path)

        painter.setPen(self._pen_selected if self.isSelected() else self._pen)
        painter.drawPath(self.path())

    def boundingRect(self):
        return self.shape().boundingRect()

    def __str__(self) -> str:
        return class_id('NodeEdge', self)


class NodeEdge:
    def __init__(self, view, start_socket, end_socket):
        self.edge_graphics = NodeEdgeGraphics(view, start_socket, end_socket)


class NodeEdgeTmp:
    def __init__(self, view, start_socket):
        self.edge_graphics = NodeEdgeGraphics(view, start_socket, None)
