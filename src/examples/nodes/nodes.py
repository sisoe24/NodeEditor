import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QComboBox,
    QLabel,
    QTextEdit
)


from ...widgets.node_graphics import Node, NodeContent
LOGGER = logging.getLogger('nodeeditor.node_input')


class NodeExample1Content(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['foo', 'bar'])

        self.add_output('Output 1')
        self.add_output('Output 2')
        self.add_widget(QLabel('----'))
        self.add_input(QLabel('Input 1'))
        self.add_input(QLabel('Input 2'))


class NodeExample1(Node):
    title_background = Qt.red
    title = "Example Node1"

    def __init__(self, scene):
        self.node_content = NodeExample1Content()
        super().__init__(scene=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()


class NodeExample2Content(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_output('Output')
        self.add_input(QTextEdit('Random text'))


class NodeExample2(Node):
    title_background = Qt.black
    title = "Test Node"

    def __init__(self, scene):
        self.node_content = NodeExample2Content()
        super().__init__(scene=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()
