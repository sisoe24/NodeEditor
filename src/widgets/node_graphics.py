import abc
import json
import pprint
import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QPen, QColor, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsScene,
    QSpacerItem,
    QLabel,
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsProxyWidget,
    QVBoxLayout,
    QWidget
)

from src.nodes import NodesRegister, extract_output_edges
from src.widgets.node_socket import Socket
from src.utils import class_id

LOGGER = logging.getLogger('nodeeditor.master_node')


class NodeGraphics(QGraphicsItem):
    _width = 150
    _title_height = 25

    def __init__(self, base: 'Node', content: QWidget, parent=None):
        super().__init__(parent)

        self.base = base
        self.content = content

        self.node_class = str(self.base)
        self.node_id = NodesRegister.register_node(self)

        self._height = max(self.base.layout_size.height(), 50)

        self._set_flags()
        self._set_colors()
        self._draw_title()
        self._draw_content()
        self._draw_graphics()

    def delete_node(self):
        """Delete the graphics node and its input edges."""
        NodesRegister.unregister_node(self)

        for socket in self.base.input_sockets:
            if socket.has_edge():
                socket.remove_edge()

        for socket in self.base.output_sockets:
            if socket.has_edge():
                edges = socket.get_edges()
                for edge in edges:
                    socket.remove_edge(edge)

        self.scene().removeItem(self)

    def _set_colors(self):
        """Initialize the node graphics colors."""
        # TODO: initialize in init
        self._node_border = QPen(QColor('#111111'))
        self._node_selected = QPen(QColor('#DD8600'))

        self._node_background = QBrush(QColor("#FF313131"))
        self._node_title_background = QBrush(self.base.title_background)

    def _set_flags(self):
        """Initialize UI for the Node graphic content."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def _draw_title(self):
        """Set Node title."""
        # title gets created at 0,0 thats why is already inside the title box
        title_item = QGraphicsTextItem(self)

        title_item.setPlainText(self.node_id)
        # title_item.setPlainText(self.base.title)
        title_item.setDefaultTextColor(Qt.white)
        title_item.setFont(QFont('Menlo', 12))

        title_sx_padding = 15.0
        title_item.setPos(title_sx_padding, 0)
        title_item.setTextWidth(self._width - 2 * title_sx_padding)

    def _draw_content(self):
        """Set Node contents.

        Contents are set inside a QGraphicsProxyWidget in a custom geometry
        space.
        """
        self.content.setGeometry(0, self._title_height,
                                 self._width, self._height)
        gr_content = QGraphicsProxyWidget(self)
        gr_content.setWidget(self.content)

    def _draw_graphics(self):
        """Draw the node graphics content.

        This function gets called when the class gets initialized and creates
        the shape of the node graphics which are composed of 2 parts: the body,
        the title.

        """
        def draw_body():
            """Draw the main body of the node."""
            path = QPainterPath()

            width_angle = self._width - 10

            height = self._height + self._title_height
            height_angle = height - 5

            # start from right
            path.moveTo(self._width, 5.0)
            path.arcTo(width_angle, 0.0, 10.0, 10.0, 0.0, 90.0)

            # go to left
            path.lineTo(5.0, 0.0)
            path.arcTo(0, 0.0, 10.0, 10.0, 90.0, 90.0)

            # go to down
            path.lineTo(0.0, height)
            path.arcTo(0.0, height_angle, 10.0, 10.0, 180.0, 90.0)

            # go to right
            path.lineTo(width_angle, height + 5)
            path.arcTo(width_angle, height_angle, 10.0, 10.0, 270.0, 90.0)

            path.closeSubpath()
            return path

        def draw_title():
            """Draw the title body of the node."""
            path = QPainterPath()

            width_angle = self._width - 10

            # start from right
            path.moveTo(self._width, 5.0)
            path.arcTo(width_angle, 0.0, 10.0, 10.0, 0.0, 90.0)

            # go to left
            path.lineTo(5.0, 0.0)
            path.arcTo(0, 0.0, 10.0, 10.0, 90.0, 90.0)

            # go to down
            path.lineTo(0.0, self._title_height)

            # # go to right
            path.lineTo(self._width, self._title_height)

            path.closeSubpath()
            return path

        # TODO: initialize in init
        self._node_title = draw_title()
        self._node_body = draw_body()

    def paint(self, painter, option, widget=None):
        """Paint the content of the node."""

        def draw_title():
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._node_title_background)
            painter.drawPath(self._node_title)

        def draw_body():
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._node_background)
            painter.drawPath(self._node_body)

        def draw_outline():
            painter.setPen(self._node_selected if self.isSelected()
                           else self._node_border)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self._node_body)

        draw_body()
        draw_title()
        draw_outline()

    def boundingRect(self):
        """Set the bounding margins for the node."""
        return self._node_body.boundingRect()

    def data(self) -> dict:
        def get_sockets(sockets_list, is_input=False):
            sockets = {}
            for index, socket in enumerate(sockets_list):
                sockets[index] = {str(socket): {'edges': socket.get_edges()}}
            return sockets

        position = self.pos()
        return {
            'class': self.node_class,
            'object': str(self),
            'id': self.node_id,
            'zValue': self.zValue(),
            'position': {'x': position.x(), 'y': position.y()},
            # 'input_sockets': get_sockets(self.base.input_sockets, True),
            # 'output_sockets': get_sockets(self.base.output_sockets),
            'output_edges': extract_output_edges(self),
            'input_edges': {}
        }

    def repr(self):
        return pprint.pformat(self.data(), 1, 100)
        # return json.dumps(self.data(), indent=1)

    def __str__(self) -> str:
        return class_id('NodeGraphics', self)

    def __repr__(self) -> str:
        return class_id('NodeGraphics', self)

    def __lt__(self, node):
        return str(self.base) < str(node.base)


class NodeInterface(abc.ABC):

    @abc.abstractproperty
    def title(self):
        pass

    @abc.abstractproperty
    def title_background(self):
        pass

    @abc.abstractproperty
    def layout_size(self):
        pass


class Node(NodeInterface):

    def __init__(self, scene_graphics, node, content):
        LOGGER.info('Init Node')

        self.node_graphics = NodeGraphics(node, content)
        scene_graphics.addItem(self.node_graphics)

        self.input_sockets = []
        self.output_sockets = []

        self._add_inputs(node)
        self._add_outputs(node)

    def _add_sockets(self, widgets, is_input=True):
        """Add sockets to node.

        Sockets will be added at the left or right of the node based on which
        type of widgets is assign to it.

        Args:
            widgets (list): a list of widgets to assign a socket.
            is_input (bool, optional): If True, sockets will be positioned on,
            the left. If False, will be position on the right. Defaults to True.
        """
        # arbitrary offset to account for the widget position
        offset = 8
        width = self.node_graphics._width

        for index, widget in enumerate(widgets):
            y = self.node_graphics._title_height + widget.pos().y() + offset

            socket = Socket(self.node_graphics, index, is_input)
            socket.setPos(0 if is_input else width, y)

            yield socket

    def _add_inputs(self, node):
        for socket in self._add_sockets(node.node_content.inputs):
            self.input_sockets.append(socket)

    def _add_outputs(self, node):
        for socket in self._add_sockets(node.node_content.outputs, False):
            self.output_sockets.append(socket)

    def set_position(self, x: int, y: int):
        self.node_graphics.setPos(x, y)

    def __str__(self):
        return f'{self.__class__.__name__}'
