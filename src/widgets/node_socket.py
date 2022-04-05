
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPen, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsItem
)

from src.utils import class_id
from src.widgets.node_edge import NodeEdge


class SocketGraphics(QGraphicsItem):
    def __init__(self, node,  index, is_input, parent=None):
        super().__init__(node)

        self._node = node
        self._index = index
        self._is_input = is_input

        self._outline_pen = QPen(Qt.black)
        self._outline_pen.setWidthF(0.5)

        self._color = Qt.red
        if self._is_input:
            self._color = Qt.green

        self._edge = None

        self._draw_graphics()
        self._set_flags()

    def is_connected(self):
        return bool(self.edge)

    def is_input(self):
        return self._is_input

    @property
    def node(self):
        return self._node

    @property
    def index(self):
        return self._index

    @property
    def edge(self):
        return self._edge

    @edge.setter
    def edge(self, edge: NodeEdge):
        self._edge = edge

    def has_edge(self):
        return bool(self.edge)

    def remove_edge(self):
        self.scene().removeItem(self.edge.edge_graphics)
        self.edge.clear_reference()
        self.edge = None

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
        painter.setBrush(QBrush(self._color))
        painter.setPen(self._outline_pen)
        painter.drawPath(self._socket_body)

    def boundingRect(self):
        return self._socket_body.boundingRect()

    def __str__(self) -> str:
        return class_id('SocketGraphics', self)

    def get_position(self):
        """Get socket position in the scene."""
        return self.scenePos()


class Socket:
    def __init__(self, node, index, is_input):
        self.socket_graphics = SocketGraphics(node, index, is_input)

    def get_position(self):
        """Get socket position in the scene."""
        return self.socket_graphics.scenePos()
