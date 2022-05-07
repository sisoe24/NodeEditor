
import json
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPen, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsItem
)

from src.utils import class_id


class SocketObject:
    def __init__(self, parent_node, socket_index, socket_data, widget):

        self.parent_node = parent_node
        self.socket_index = socket_index
        self.socket_data = socket_data
        self.socket_widget = widget


def create_socket(parent_node, socket_index, socket_data, widget, node_side):
    socket = SocketObject(parent_node, socket_index, socket_data, widget)

    if node_side == 'left':
        return SocketInput(socket)

    return SocketOutput(socket)


class SocketType:

    execute = {'type': 'execute', 'color': QColor('#FFFFFF')}
    number = {'type': 'number', 'color': QColor('#D19A66')}
    array = {'type': 'list', 'color': QColor('#18B2A5')}
    boolean = {'type': 'boolean', 'color': QColor('#BD74D3')}
    text = {'type': 'string', 'color': QColor('#98C379')}
    widget = {'type': 'widget', 'color': QColor('#BD0015')}
    value = {'type': 'value', 'color': QColor('#BDFF45')}

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

        self.color = self.socket_type['color']

        if self.socket_type == self.array:
            path = QPainterPath()
            path.addRect(-6, -6, 10, 10)
            return path

        if self.socket_type == self.execute:
            path = QPainterPath()
            path.moveTo(7.0, 0.0)
            path.lineTo(0.0, -7.0)
            path.lineTo(-7.0, -0.0)
            path.lineTo(0.0, 7.0)
            return path

        return self._draw_ellipse()


class SocketGraphics(QGraphicsItem):
    def __init__(self, socket):
        super().__init__(socket.parent_node)

        self._socket = socket

        self._socket_data = socket.socket_data

        self._socket_body = SocketType(socket.socket_data.data)
        self.color = self._socket_body.color

        self._outline_pen = QPen(Qt.black)
        self._outline_pen.setWidthF(0.5)

        self._set_flags()

        self.setToolTip(self.socket_type.title())

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

    @property
    def socket_type(self):
        return self._socket_data.data['type']

    @property
    def label(self):
        return self._socket_data.label

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

    def data(self, key=None) -> str:
        edges = str(self.edge) if isinstance(self, SocketInput) else [
            str(edge) for edge in self.edges]

        socket_data = {
            'object': str(self),
            'index': self.index,
            'widget': str(self.widget),
            'node': str(self.node),
            'type': self.socket_type,
            'color': self._socket_data.data['color'].name(),
            'label': self.label,
            'edges': edges
        }

        return socket_data.get(key, socket_data)

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
