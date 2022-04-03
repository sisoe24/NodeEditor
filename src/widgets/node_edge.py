import abc
import logging

from PySide2.QtCore import QPointF,  Qt
from PySide2.QtGui import QPen, QPainterPath, QColor, QPainterPathStroker

from PySide2.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItem,
)

from src.utils import class_id

LOGGER = logging.getLogger('nodeeditor.edge')
LOGGER.setLevel(logging.DEBUG)


class NodeEdgeGraphics(QGraphicsPathItem):

    def __init__(self, edge):
        super().__init__(edge.start_point)
        LOGGER.debug('Creating edge')

        self.edge = edge

        self._mouse_position = self.mapToScene(QPointF(0, 0))
        self.edge._view.mouse_position.connect(self._set_mouse)

        self._set_colors()
        self._set_flags()

    def delete_edge(self):
        """Delete the graphic edge and remove its reference from siblings nodes."""
        self.edge.clear_end_points()
        self.scene().removeItem(self)

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

        if self.edge.end_point:
            end = self.mapFromScene(self.edge.end_point.get_position())
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


class _EdgeInterface(abc.ABC):

    @property
    @abc.abstractmethod
    def start_point(self):
        pass

    @property
    def end_point(self):
        return None


class NodeEdge(_EdgeInterface):
    def __init__(self, view, start_socket, end_socket):

        self._start_socket = start_socket
        self._end_socket = end_socket
        self._view = view

        self.edge_graphics = NodeEdgeGraphics(self)
        self._add_end_points()

    @property
    def start_point(self):
        return self._start_socket

    @property
    def end_point(self):
        return self._end_socket

    def clear_end_points(self):
        # TODO: might need to clean a specific edge when multiple are present
        self.start_point.parentItem()._edges.clear()
        self.end_point.parentItem()._edges.clear()

    def _add_end_points(self):
        """Add the edge to the end points.

        When creating the edge, automatically add its reference to the end points
        (starting socket and end socket) `edges` attribute. This is to be able
        to have a reference when deleting the nodes.
        """
        self._end_socket.parentItem().add_edge(self)
        self._start_socket.parentItem().add_edge(self)


class NodeEdgeTmp(_EdgeInterface):
    def __init__(self, view, start_socket):

        self._start_socket = start_socket
        self._view = view
        self.edge_graphics = NodeEdgeGraphics(self)

    @property
    def start_point(self):
        return self._start_socket
