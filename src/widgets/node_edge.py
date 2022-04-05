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

        self.edge = edge

        self._set_colors()
        self._set_flags()

    def delete_edge(self):
        """Delete the graphic edge and remove its reference from siblings nodes."""
        self.edge.clear_reference()

        # FIXME: temporary solution when deleting a node before and edge
        # in a multi selection. because the node removes the edge, the selection
        # still keeps a reference to it, so calling it will result in the scene.
        # not being found.
        try:
            self.scene().removeItem(self)
        except AttributeError as err:
            LOGGER.warning(
                'Could not delete edge: %s. It might have been already deleted. Error: %s', self, err)

    def _set_colors(self):
        self._pen_selected = QPen(QColor('#DD8600'))
        self._pen_selected.setWidthF(2.0)

        self._pen = QPen(QColor("#001000"))
        self._pen.setWidthF(2.0)

    def _set_flags(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent)

    def paint(self, painter, option, widget=None):
        """Paint the edge between the nodes."""
        path = QPainterPath(QPointF(0, 0))
        path.lineTo(self.mapFromScene(self.edge.end_point_loc))

        stroke = QPainterPathStroker()
        stroke.setJoinStyle(Qt.RoundJoin)
        stroke.setWidth(1.5)
        stroker_path = stroke.createStroke(path)
        self.setPath(stroker_path)

        painter.setPen(self._pen_selected if self.isSelected() else self._pen)
        painter.drawPath(self.path())

    def boundingRect(self):
        return self.shape().boundingRect()

    def __str__(self) -> str:
        return class_id('NodeEdgeGraphics', self)


class _EdgeInterface(abc.ABC):

    @property
    @abc.abstractmethod
    def start_point(self):
        """Start point Socket."""

    @property
    def end_point(self):
        """End point Socket."""
        return None

    @property
    @abc.abstractmethod
    def end_point_loc(self):
        """End point scene location."""


class NodeEdge(_EdgeInterface):
    def __init__(self, view, start_socket, end_socket):

        LOGGER.debug('Create connected edge')

        self._start_socket = start_socket
        self._end_socket = end_socket
        self._view = view

        self.edge_graphics = NodeEdgeGraphics(self)
        self._add_reference_points()

    @property
    def start_point(self):
        return self._start_socket

    @property
    def end_point(self):
        return self._end_socket

    @property
    def end_point_loc(self):
        return self.end_point.get_position()

    def clear_reference(self):
        """Remove Edge reference inside the Node edge list."""
        self.start_point.parentItem().remove_edge(self)
        self.end_point.parentItem().remove_edge(self)

        self.start_point._edges = []
        self.end_point._edges = []

    def _add_reference_points(self):
        """Add the edge to the end points.

        When creating the edge, automatically add its reference to the end points
        (starting socket and end socket) `edges` attribute. This is to be able
        to have a reference when deleting the nodes.
        """
        self.start_point.add_edge(self)
        self.end_point.add_edge(self)

        self.start_point.parentItem().add_edge(self)
        self.end_point.parentItem().add_edge(self)

    def __del__(self):
        # Review: how to make it work
        print('Delete NodeEdge')

    def __str__(self) -> str:
        return class_id('NodeEdge', self)


class NodeEdgeTmp(_EdgeInterface):
    def __init__(self, view, start_socket):
        LOGGER.debug('Create temporary edge')

        self._mouse_position = QPointF(start_socket.get_position().x(),
                                       start_socket.get_position().y())
        view.mouse_position.connect(self._set_end_point_loc)

        self._start_socket = start_socket
        self._view = view
        self.edge_graphics = NodeEdgeGraphics(self)

    @property
    def start_point(self):
        return self._start_socket

    @property
    def end_point_loc(self):
        return self._mouse_position

    def _set_end_point_loc(self, x, y):
        self._mouse_position = QPointF(x, y)

    def __str__(self) -> str:
        return class_id('NodeEdgeTmp', self)
