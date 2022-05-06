
import json
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPen, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsItem
)
from src.sockets.sockets_types import SocketType

from src.utils import class_id


class SocketObject:
    def __init__(self, parent_node, socket_index, socket_type, widget):

        self.parent_node = parent_node
        self.socket_index = socket_index
        self.socket_type = socket_type
        self.socket_widget = widget


def create_socket(parent_node, socket_index, socket_type, widget, node_side):
    socket = SocketObject(parent_node, socket_index, socket_type, widget)

    if node_side == 'left':
        return SocketInput(socket)

    if node_side == 'right':
        return SocketOutput(socket)


class SocketPath:
    def __init__(self, socket_type):
        self.color = Qt.white

        self.socket_type = socket_type
        self.path = self.draw_socket()

    @staticmethod
    def _draw_ellipse():
        path = QPainterPath()
        radius = 6.0
        path.addEllipse(-radius, -radius, radius * 2, radius * 2)
        return path

    def draw_socket(self):
        if self.socket_type == SocketType.array:
            self.color = QColor('#F2A19D')
            path = QPainterPath()
            path.addRect(-6, -6, 10, 10)
            return path

        if self.socket_type == SocketType.execute:
            path = QPainterPath()
            path.moveTo(7.0, 0.0)
            path.lineTo(0.0, -7.0)
            path.lineTo(-7.0, -0.0)
            path.lineTo(0.0, 7.0)
            return path

        if self.socket_type == SocketType.widget:
            self.color = QColor('#BD0015')

        if self.socket_type == SocketType.boolean:
            self.color = QColor('#BD74D3')

        if self.socket_type == SocketType.text:
            self.color = QColor('#98C379')

        if self.socket_type == SocketType.number:
            self.color = QColor('#D19A66')

        return self._draw_ellipse()


class SocketGraphics(QGraphicsItem):
    def __init__(self, socket):
        super().__init__(socket.parent_node)

        self._socket = socket

        self.socket_type = socket.socket_type
        self.setToolTip(self.socket_type.title())

        self._socket_body = SocketPath(self.socket_type)
        self.color = self._socket_body.color

        self._outline_pen = QPen(Qt.black)
        self._outline_pen.setWidthF(0.5)

        self._set_flags()

    def get_position(self):
        """Get socket position in the scene."""
        return self.scenePos()

    @property
    def node(self):
        return self._socket.parent_node

    @property
    def index(self):
        return self._socket.socket_index

    @property
    def widget(self):
        return self._socket.socket_widget

    def _set_flags(self):
        """Initialize UI for the Node graphic content."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(self._outline_pen)
        painter.drawPath(self._socket_body.path)

    def boundingRect(self):
        return self._socket_body.path.boundingRect()

    def __str__(self) -> str:
        return class_id('SocketGraphics', self)

    def __repr__(self) -> str:
        return class_id('SocketGraphics', self)

    def data(self) -> str:
        edges = str(self.edge) if isinstance(self, SocketInput) else [
            str(edge) for edge in self.edges]

        return {
            'type': str(self.socket_type),
            'object': str(self),
            'index': self._index,
            'widget': str(self._widget),
            'color': self.color.name.decode('utf-8'),
            'node': str(self.node),
            'edges': edges
        }

    def repr(self):
        # return pprint.pformat(self.data(), 1, 100)
        return json.dumps(self.data(), indent=1)


class SocketInput(SocketGraphics):

    def __init__(self, socket):
        super().__init__(socket)
        self._edge = None

    @property
    def edge(self):
        return self._edge

    def has_edge(self):
        return bool(self._edge)

    def get_edges(self):
        return self.edge

    def add_edge(self, edge):
        self._edge = edge

    def clear_reference(self):
        self._edge = None

    def remove_edge(self):
        self.edge.delete_edge()

    def __str__(self) -> str:
        return class_id('SocketInput', self)


class SocketOutput(SocketGraphics):

    def __init__(self, socket):
        super().__init__(socket)
        self._edges = []

    @property
    def edges(self):
        return self._edges

    def add_edge(self, edge: 'NodeEdge'):
        self._edges.append(edge)

    def get_edges(self):
        """Return the socket edges.

        Returns:
            list: a shallow copy of the socket edge list.
        """
        return self.edges.copy()

    def has_edge(self):
        return bool(self._edges)

    def remove_edge(self, edge):
        edge = self.edges.index(edge)
        self.edges[edge].delete_edge()

    def clear_reference(self, edge):
        self._edges.remove(edge)

    def __str__(self) -> str:
        return class_id('SocketOutput', self)
