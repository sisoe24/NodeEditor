import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QRadioButton,
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

        self.add_output('Output', pos=0)

        self.make_upper = QRadioButton('Make Uppercase')
        self.make_upper.setChecked(True)
        self.add_widget(self.make_upper, pos=1)

        self.make_lower = QRadioButton('Make Lowercase')
        self.add_widget(self.make_lower, pos=2)

        self.make_title = QRadioButton('Make Titlecase')
        self.add_widget(self.make_title, pos=3)

        self.add_input(QLabel('Input'), pos=4)

        self.output_text = None

    def get_output(self, index):
        return self.output_text or "Sample Text"

    def set_input(self, value, index):

        if self.make_upper.isChecked():
            self.output_text = value.upper()
        elif self.make_lower.isChecked():
            self.output_text = value.lower()
        elif self.make_title.isChecked():
            self.output_text = value.title()
        else:
            self.output_text = value

        # print("➡ self.output_text :", self.output_text)


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
        self.checkbox = QCheckBox('Save render')
        self.add_input(self.checkbox)

    def get_output(self, index):
        return "Output from test node"

    def set_input(self, value, index):
        self.checkbox.setChecked(bool(value))
        return "Output from test node"


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

        self.text_box = QPlainTextEdit('foo BAR')

        self.add_output('Text', pos=0)
        self.add_output('Random Text', pos=1)
        self.add_widget(self.text_box, pos=2)

    def get_output(self, index=1):

        if index == 0:
            return self.text_box.toPlainText()

        if index == 1:
            return str(len(self.text_box.toPlainText()))

        return ""


@NodesRegister.register_class
class NodeInput(Node):
    title_background = Qt.blue
    title = 'Input Node'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeInputContent())
