import abc
import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QPen, QColor, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QSpacerItem,
    QLabel,
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsProxyWidget,
    QVBoxLayout,
    QWidget
)

from src.widgets.node_socket import Socket
from src.utils import class_id

LOGGER = logging.getLogger('nodeeditor.master_node')


class NodeContent(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.inputs = []
        self.outputs = []

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.addSpacerItem(QSpacerItem(0, 0))
        self._layout.setSpacing(15)
        self.setLayout(self._layout)

    def __str__(self) -> str:
        return f"<Socket {hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"

    def _is_widget(func):
        def wrapper(*args):
            widget = args[1]
            if isinstance(widget, QWidget):
                return func(*args)
            LOGGER.error('Item is not a Widget: %s', widget)
        return wrapper

    @_is_widget
    def add_widget(self, widget):
        """Add a widget into the node graphics

        A widget is not going to have any input or output sockets connected.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self._layout.addWidget(widget)

    @_is_widget
    def add_input(self, widget):
        """Add an input widget with a socket.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self.inputs.append(widget)
        self._layout.addWidget(widget)

    def add_output(self, text: str):
        """Add an output widget with a socket.

        Args:
            text (str): The name of the output label
        """
        widget = QLabel(text)
        widget.setAlignment(Qt.AlignRight)
        self._layout.addWidget(widget)
        self.outputs.append(widget)


class NodeGraphics(QGraphicsItem):
    _width = 150
    _title_height = 25

    def __init__(self, node: 'Node', content: QWidget, parent=None):
        super().__init__(parent)

        self.node = node
        self.content = content

        self._height = max(self.node.layout_size.height(), 50)

        self._set_flags()
        self._set_colors()
        self._draw_title()
        self._draw_content()
        self._draw_graphics()

    def _set_colors(self):
        """Initialize the node graphics colors."""
        # TODO: initialize in init
        self._node_border = QPen(QColor('#111111'))
        self._node_selected = QPen(QColor('#DD8600'))

        self._node_background = QBrush(QColor("#FF313131"))
        self._node_title_background = QBrush(self.node.title_background)

    def _set_flags(self):
        """Initialize UI for the Node graphic content."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def _draw_title(self):
        """Set Node title."""
        # title gets created at 0,0 thats why is already inside the title box

        # Review: don't know what its doing
        # self._title_item.node = self.node
        title_item = QGraphicsTextItem(self)

        title_item.setPlainText(self.node.title)
        title_item.setDefaultTextColor(Qt.white)
        title_item.setFont(QFont('Menlo', 14))

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

    def __str__(self) -> str:
        return class_id('NodeGraphics', self)


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

    def __init__(self, scene, node, content):
        LOGGER.info('Init Node')

        self.node_graphics = NodeGraphics(node, content)
        scene.graphics_scene.addItem(self.node_graphics)

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

        for widget in widgets:
            y = self.node_graphics._title_height + widget.pos().y() + offset

            socket = Socket(self.node_graphics)
            socket.socket_graphics.setPos(0 if is_input else width, y)

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
