import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QPushButton,
    QTextEdit,
    QLabel,
)
from src.widget_color import widget_color

from src.widgets.master_node import Node, NodeContentCreator
LOGGER = logging.getLogger('nodeeditor.node_test')


class NodeContent(NodeContentCreator):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_widget(QLabel('Some Title'))
        self.add_widget(QPushButton('Click me'))
        self.add_widget(QPushButton('Click you'))
        self.add_widget(QTextEdit('Random text'))


class NodeTest(Node):
    title_background = Qt.black
    title = "Test Node"

    def __init__(self, scene):
        self.node_content = NodeContent()
        super().__init__(scene=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()
