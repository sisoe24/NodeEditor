
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPen, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsItem
)

from src.utils import class_id
from src.widgets.node_edge import NodeEdge


class SocketGraphics(QGraphicsItem):
    def __init__(self, node,  index):
        super().__init__(node)

        self._node = node
        self._index = index

        self._outline_pen = QPen(Qt.black)
        self._outline_pen.setWidthF(0.5)

        self._draw_graphics()
        self._set_flags()

    @property
    def node(self):
        return self._node

    @property
    def index(self):
        return self._index

    def _set_flags(self):
        """Initialize UI for the Node graphic content."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def _draw_graphics(self):
        """Draw the graphics of the socket ellipse."""
        path = QPainterPath()
        radius = 6.0
        path.addEllipse(-radius, -radius, radius * 2, radius * 2)
        self._socket_body = path

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(self._outline_pen)
        painter.drawPath(self._socket_body)

    def boundingRect(self):
        return self._socket_body.boundingRect()

    def __str__(self) -> str:
        return class_id('SocketGraphics', self)

    def get_position(self):
        """Get socket position in the scene."""
        return self.scenePos()


class SocketInput(SocketGraphics):
    color = Qt.green

    def __init__(self, node, index):
        super().__init__(node, index)
        self._edge = None

    @property
    def edge(self):
        return self._edge

    def has_edge(self):
        return bool(self._edge)

    def add_edge(self, edge: NodeEdge):
        self._edge = edge

    def clear_reference(self, edge):
        self._edge = None

    def remove_edge(self):
        self.edge.edge_graphics.delete_edge()

    def __str__(self) -> str:
        return class_id('SocketInput', self)


class SocketOutput(SocketGraphics):
    color = Qt.blue

    def __init__(self, node, index):
        super().__init__(node, index)
        self._edges = []

    @property
    def edges(self):
        return self._edges

    def add_edge(self, edge: NodeEdge):
        self._edges.append(edge)

    def clear_reference(self, edge):
        self._edges.remove(edge)

    def __str__(self) -> str:
        return class_id('SocketOutput', self)


class Socket:
    def __init__(self, node, index, is_input):
        if is_input:
            self.socket_graphics = SocketInput(node, index)
        else:
            self.socket_graphics = SocketOutput(node, index)

    def get_position(self):
        """Get socket position in the scene."""
        return self.socket_graphics.scenePos()
