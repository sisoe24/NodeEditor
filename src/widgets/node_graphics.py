import abc
import logging

from PySide2.QtCore import Signal, Qt, QRectF
from PySide2.QtGui import QPainterPathStroker, QFont, QPen, QColor, QPainterPath, QBrush
from PySide2.QtWidgets import (
    QLabel,
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsProxyWidget,
    QVBoxLayout,
    QWidget
)

LOGGER = logging.getLogger('nodeeditor.master_node')


class NodeContent(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = QVBoxLayout()
        # self._layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self._layout)

    def add_widget(self, widget: QWidget):
        self._layout.addWidget(widget)

    def add_input(self, widget: QWidget):
        self._layout.addWidget(widget)

    def add_output(self, text: str):
        widget = QLabel(text)
        widget.setAlignment(Qt.AlignRight)
        self._layout.addWidget(widget)


class NodeGraphics(QGraphicsItem):
    _width = 150
    _title_height = 25

    def __init__(self, node: 'Node', content: QWidget, parent=None):
        super().__init__(parent)
        LOGGER.info('Node graphics')

        self.node = node
        self.content = content

        self._height = max(self.node.layout_size.height(), 50)

        self._set_flags()
        self._set_colors()
        self._init_title()
        self._init_content()
        self._draw_graphics()

    def _set_colors(self):
        self._node_border = QPen(QColor('#111111'))
        self._node_selected = QPen(QColor('#DD8600'))

        self._node_background = QBrush(QColor("#FF313131"))
        self._node_title_background = QBrush(self.node.title_background)

    def _set_flags(self):
        """Initialize UI for the Node graphic content."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def _init_title(self):
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

    def _init_content(self):
        """Set Node contents.

        Contents are set inside a QGraphicsProxyWidget in a custom geometry
        space.
        """
        self.content.setGeometry(0, self._title_height,
                                 self._width, self._height)
        gr_content = QGraphicsProxyWidget(self)
        gr_content.setWidget(self.content)

    def _draw_graphics(self):
        def draw_body():
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
        return QRectF(0, 0, self._width, self._height).normalized()


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

    def set_position(self, x: int, y: int):
        self.node_graphics.setPos(x, y)
