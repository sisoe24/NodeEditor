import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QSpinBox,
    QPlainTextEdit,
    QCheckBox,
    QComboBox,
    QLabel,
)


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node

LOGGER = logging.getLogger('nodeeditor.nodes_example')


class NodeExampleContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['foo', 'bar'])

        self.add_output('Output 1')

        self.add_widget(QCheckBox('Make Uppercase'))
        self.add_widget(QCheckBox('Make Lowercase'))
        self.add_widget(QCheckBox('Make Titlecase'))
        self.add_input(QLabel('Input 1'), 0)


@NodesRegister.register_class
class NodeExample(Node):
    title_background = Qt.red
    title = "Example Node"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeExampleContent())


class NodeDebugContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_box = QPlainTextEdit()
        self.add_label('Debug Print', pos=0)
        self.add_input_widget(self.text_box, pos=1)
        self.add_input_widget(QPlainTextEdit(), pos=2)

    def set_input(self, value, index):
        self.inputs[index].setPlainText(value)


@NodesRegister.register_class
class NodeDebug(Node):
    title_background = Qt.green
    title = "Debug Node"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeDebugContent())


class NodeTestContent(NodeContent):
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
        super().__init__(scene=scene, node=self, content=NodeTestContent())


class NodeInputContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_box = QPlainTextEdit('foo far')

        self.add_widget(self.text_box)
        self.add_output('Output 1', 0)

    def get_output(self):
        return self.text_box.toPlainText()


@NodesRegister.register_class
class NodeInput(Node):
    title_background = Qt.blue
    title = 'Input Node'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeInputContent())
