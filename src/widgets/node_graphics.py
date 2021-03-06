import abc
import pprint
import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QPen, QColor, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsProxyWidget,
    QWidget
)

from src.nodes import NodesRegister, extract_output_edges, extract_input_edges
from src.utils import class_id
from src.widgets.node_socket import create_socket

LOGGER = logging.getLogger('nodeeditor.master_node')


class NodeGraphicsContent(QGraphicsProxyWidget):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWidget(content)

    def __str__(self):
        return class_id('NodeGraphicsContent', self)


class NodeGraphics(QGraphicsItem):
    _width = 150
    _title_height = 25

    def __init__(self, base: 'Node', content: QWidget, parent=None):
        super().__init__(parent)

        self.base = base
        self.content = content
        self.node_class = str(self.base)
        self.node_id = NodesRegister.register_node(self)

        self._height = max(self.content.layout_size.height(), 50)

        self._set_flags()
        self._set_colors()
        self._draw_title()
        self._draw_content()
        self._draw_graphics()

    def delete_node(self):
        """Delete the graphics node and its input edges."""
        NodesRegister.unregister_node(self)

        # Merge two dicts. I would rather use .update but does not work
        edges = {**self.data('input_edges'), **self.data('output_edges')}
        for edge in edges:
            edge.delete_edge()

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

        # title_item.setPlainText(self.node_id)
        title_item.setPlainText(self.base.title)
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
        NodeGraphicsContent(self.content, self)

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

    def data(self, key=None) -> dict:

        position = self.pos()
        node_data = {
            'class': self.node_class,
            'object': str(self),
            'id': self.node_id,
            'zValue': self.zValue(),
            'position': {'x': position.x(), 'y': position.y()},
            'output_edges': extract_output_edges(self),
            'input_edges': extract_input_edges(self),
            'node_output': self.base.get_output(),
            'connected_sockets': {
                'input_sockets': {},
                'output_sockets': {}
            }
        }
        return node_data.get(key, node_data)

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

    is_event_node = None

    @property
    @abc.abstractmethod
    def title(self):
        pass

    @property
    @abc.abstractmethod
    def title_background(self):
        pass


class Node(NodeInterface):

    def __init__(self, scene, node, content):
        LOGGER.info('Init Node')

        self.content = content

        self.node_graphics = NodeGraphics(node, content)
        scene.addItem(self.node_graphics)

        self.input_sockets = []
        self.output_sockets = []
        self.output_execs = []

        self.was_execute = False

        self._add_inputs()
        self._add_outputs()

    def _add_sockets(self, widgets, node_side):
        """Add sockets to node.

        Sockets will be added at the left or right of the node based on which
        type of widgets is assign to it.

        Args:
            widgets (list): a list of widgets to assign a socket.
            node_side (str): socket type
            the left. If False, will be position on the right. Defaults to True.
        """
        # arbitrary offset to account for the widget position
        offset = 8
        node_width = self.node_graphics._width

        for index, socket_data in enumerate(widgets):

            widget = socket_data.widget

            socket = create_socket(
                self.node_graphics, index, socket_data, widget, node_side
            )

            y = self.node_graphics._title_height + widget.pos().y() + offset
            socket.setPos(0 if node_side == 'left' else node_width, y)

            yield (socket, socket_data.data['type'])

    def _add_inputs(self):
        for socket, _ in self._add_sockets(self.content.inputs, 'left'):
            self.input_sockets.append(socket)

    def _add_outputs(self):
        for socket, socket_type in self._add_sockets(self.content.outputs, 'right'):
            self.output_sockets.append(socket)

            if socket_type == 'execute':
                self.output_execs.append(socket)

    def set_position(self, x: int, y: int):
        self.node_graphics.setPos(x, y)

    def get_output(self, index=0):
        return self.content.get_output(index)

    def set_input(self, value, index=0):
        self.content.set_input(value, index)

        for edge in self.node_graphics.data('output_edges'):
            if edge.start_socket.socket_type == 'execute':
                continue
            edge.transfer_data()

        self.was_execute = True

    def get_execute_flow(self):
        return self.content.get_execute_flow(self.output_execs)

    def __str__(self):
        return f'{self.__class__.__name__}'
