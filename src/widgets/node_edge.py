import abc
import json
import logging

from PySide2.QtCore import QPointF,  Qt
from PySide2.QtGui import QPen, QPainterPath, QColor, QPainterPathStroker

from PySide2.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItem,
)

from src.utils import class_id
from src.widgets.node_socket import SocketInput, SocketOutput

LOGGER = logging.getLogger('nodeeditor.edge')
LOGGER.setLevel(logging.DEBUG)


class NodeEdgeGraphics(QGraphicsPathItem):

    def __init__(self, base, parent=None):
        super().__init__(parent)

        self.base = base

        self._set_colors()
        self._set_flags()

    def _set_colors(self):
        self._pen_selected = QPen(QColor('#DD8600'))
        self._pen_selected.setWidthF(2.0)

        self._pen = QPen(QColor("#001000"))
        self._pen.setWidthF(2.0)

    def _set_flags(self):
        # Review: I might not need to select the edge
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.setZValue(-5.0)

    def paint(self, painter, option, widget=None):
        """Paint the edge between the nodes."""
        path = QPainterPath(self.base.start_socket.get_position())
        path.lineTo(self.mapFromScene(self.base.end_point_loc))

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

    def data(self, key=None) -> str:
        edge_data = {
            'id': str(self),
            'class_id': str(self.base),
            'start_socket': {
                'node': str(self.base.start_socket.node),
                'socket': str(self.base.start_socket),
                'index': str(self.base.start_socket.index)
            },
            'end_socket': {
                'node': str(self.base.end_socket.node),
                'socket': str(self.base.end_socket),
                'index': str(self.base.end_socket.index)
            },
        }

        return edge_data.get(key, edge_data)

    def __repr__(self):
        return str(self)

    def repr(self):
        return json.dumps(self.data(), indent=2)


class _EdgeInterface(abc.ABC):

    @property
    @abc.abstractmethod
    def start_socket(self):
        """Start point Socket."""

    @property
    def end_socket(self):
        """End point Socket."""
        return None

    @property
    @abc.abstractmethod
    def end_point_loc(self):
        """End point scene location."""

    @abc.abstractmethod
    def delete_edge(self):
        """End point scene location."""


class NodeEdge(_EdgeInterface):
    def __init__(self, scene, start_socket: SocketInput, end_socket: SocketOutput):

        LOGGER.debug('Create connected edge')

        self._start_socket = start_socket
        self._end_socket = end_socket

        self.scene = scene

        self.edge_graphics = NodeEdgeGraphics(self)
        self.scene.addItem(self.edge_graphics)

        self._add_reference()
        # self.transfer_data()

    def transfer_data(self):

        self.socket_output = self.start_socket.node.base.get_output(
            self.start_socket.index)

        self.end_socket.node.base.set_input(
            self.socket_output, self.end_socket.index)

    @property
    def start_socket(self) -> SocketOutput:
        return self._start_socket

    @property
    def end_socket(self) -> SocketInput:
        return self._end_socket

    @property
    def end_point_loc(self):
        return self.end_socket.get_position()

    def delete_edge(self):
        """Delete the graphic edge.

        Remove the edge graphics from the scene and delete its reference from
        its connected sockets.
        """
        # start socket is always a SocketOutput, which has a list of edges
        # thus a reference to the deleted edge is needed
        self.start_socket.clear_reference(self)

        # end socket is always a SocketInput, which has only one edge
        self.end_socket.clear_reference()

        self.scene.removeItem(self.edge_graphics)

    def _add_reference(self):
        """Add the edge reference to socket list."""
        self.start_socket.add_edge(self)
        self.end_socket.add_edge(self)

    def __str__(self) -> str:
        return class_id('NodeEdge', self)


class NodeEdgeTmp(_EdgeInterface):
    def __init__(self, scene, view, start_socket):
        LOGGER.debug('Create temporary edge')

        self._mouse_position = QPointF(start_socket.get_position().x(),
                                       start_socket.get_position().y())
        view.mouse_position.connect(self._set_end_point_loc)

        self._start_socket = start_socket

        self.scene = scene

        self.edge_graphics = NodeEdgeGraphics(self)
        self.scene.addItem(self.edge_graphics)

    @property
    def start_socket(self):
        return self._start_socket

    @property
    def end_point_loc(self):
        return self._mouse_position

    def _set_end_point_loc(self, x, y):
        self._mouse_position = QPointF(x, y)

    def delete_edge(self):
        """Delete the graphic edge."""
        self.scene.removeItem(self.edge_graphics)

    def __str__(self) -> str:
        return class_id('NodeEdgeTmp', self)
