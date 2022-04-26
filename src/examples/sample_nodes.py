import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
)


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node

LOGGER = logging.getLogger('nodeeditor.nodes_example')


class _NodeExampleContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['foo', 'bar'])

        self.add_output('Output 1')
        self.add_output('Output 2')
        self.add_output('Output 3')
        self.add_widget(QLabel('----'))
        self.add_input(QLabel('Input 1'))
        self.add_input(QLabel('Input 2'))


@NodesRegister.register_class
class NodeExample(Node):
    title_background = Qt.red
    title = "Example Node"

    def __init__(self, scene):
        self.node_content = _NodeExampleContent()
        super().__init__(scene_graphics=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()


class _NodeDebugContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_output('Debug Output')
        self.add_input(QLabel('Debug Input 1'))
        self.add_input(QLabel('Debug Input 2'))
        self.add_input(QLabel('Debug Input 3'))


@NodesRegister.register_class
class NodeDebug(Node):
    title_background = Qt.green
    title = "Debug Node"

    def __init__(self, scene):
        self.node_content = _NodeDebugContent()
        super().__init__(scene_graphics=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()


class _NodeTestContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_output('Output 1')
        self.add_output('Output 2')
        self.add_output('Output 3')
        self.add_input(QCheckBox('Random text'))


@NodesRegister.register_class
class NodeTest(Node):
    title_background = Qt.black
    title = "Test Node"

    def __init__(self, scene):
        self.node_content = _NodeTestContent()
        super().__init__(scene_graphics=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()
