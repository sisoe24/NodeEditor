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
from src.widgets.node_socket import Socket, SocketInput, SocketOutput

LOGGER = logging.getLogger('nodeeditor.edge')
LOGGER.setLevel(logging.DEBUG)


class NodeEdgeGraphics(QGraphicsPathItem):

    def __init__(self, edge):
        super().__init__(edge.start_socket)

        self.edge = edge

        self._set_colors()
        self._set_flags()

    def delete_edge(self):
        """Delete the graphic edge.

        Remove the edge graphics from the scene and delete its reference from
        its connected sockets.
        """
        self.edge.start_socket.clear_reference(self.edge)
        self.edge.end_socket.clear_reference()
        self.scene().removeItem(self)
        # del self.edge

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

    def info(self) -> str:
        return {
            'id': str(self),
            'start_socket': {
                'node': str(self.edge.start_socket.node),
                'socket': str(self.edge.start_socket),
                'index': str(self.edge.start_socket.index)
            },
            'end_socket': {
                'node': str(self.edge.end_socket.node),
                'socket': str(self.edge.end_socket),
                'index': str(self.edge.end_socket.index)
            },
        }

    def __repr__(self):
        return str(self)

    def repr(self):
        return json.dumps(self.info(), indent=2)

    # def __del__(self):
    #     print('Sorry to see you go bro')


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


class NodeEdge(_EdgeInterface):
    def __init__(self, start_socket: SocketInput, end_socket: SocketOutput):

        LOGGER.debug('Create connected edge')

        self._start_socket = start_socket
        self._end_socket = end_socket

        self.edge_graphics = NodeEdgeGraphics(self)
        self._add_reference()

    @property
    def start_socket(self) -> SocketOutput:
        return self._start_socket

    @property
    def end_socket(self) -> SocketInput:
        return self._end_socket

    @property
    def end_point_loc(self):
        return self.end_socket.get_position()

    def _add_reference(self):
        """Add the edge reference to socket list."""
        self.start_socket.add_edge(self)
        self.end_socket.add_edge(self)

    # def __del__(self):
    #     # Review: how to make it work
    #     print('Delete NodeEdge')

    def __str__(self) -> str:
        return class_id('NodeEdge', self)


class NodeEdgeTmp(_EdgeInterface):
    def __init__(self, view, start_socket: Socket):
        LOGGER.debug('Create temporary edge')

        self._mouse_position = QPointF(start_socket.get_position().x(),
                                       start_socket.get_position().y())
        view.mouse_position.connect(self._set_end_point_loc)

        self._start_socket = start_socket
        self.edge_graphics = NodeEdgeGraphics(self)

    @property
    def start_socket(self):
        return self._start_socket

    @property
    def end_point_loc(self):
        return self._mouse_position

    def _set_end_point_loc(self, x, y):
        self._mouse_position = QPointF(x, y)

    def __str__(self) -> str:
        return class_id('NodeEdgeTmp', self)
