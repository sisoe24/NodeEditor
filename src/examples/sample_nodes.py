import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QSpinBox,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QPlainTextEdit,
    QCheckBox,
    QComboBox,
)


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node

LOGGER = logging.getLogger('nodeeditor.nodes_example')


class NodeExampleContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_output_execute('Execute', pos=0)

        self.make_upper = QRadioButton('Make Uppercase')
        self.make_upper.setChecked(True)
        self.add_widget(self.make_upper, pos=1)

        self.make_lower = QRadioButton('Make Lowercase')
        self.add_widget(self.make_lower, pos=2)

        self.make_title = QRadioButton('Make Titlecase')
        self.add_widget(self.make_title, pos=3)

        self.text = QLineEdit()
        self.text.setObjectName('Text')
        self.text.setPlaceholderText('text')
        self.add_input_widget(self.text, pos=4)

        self.add_input_execute('Execute', pos=5)

        self.output_text = None

    def update_text(self, text):
        if self.make_upper.isChecked():
            return text.upper()

        if self.make_lower.isChecked():
            return text.lower()

        if self.make_title.isChecked():
            return text.title()

        return text

    def get_output(self, index):
        return self.output_text or self.update_text(self.text.text())

    def set_input(self, value, index):
        self.output_text = self.update_text(value)
        super().set_input(value, index)

    def clear_output(self, index):
        self.output_text = None


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

        self.add_input_execute(label='Print', pos=0)
        self.text_box = QPlainTextEdit()
        self.add_widget(self.text_box, pos=1)

    def set_input(self, value, index):
        super().set_input(value, index)
        self.text_box.setPlainText(value)

    def clear_output(self, index):
        return

    def get_output(self, index):
        return


@NodesRegister.register_class
class NodeDebug(Node):
    title_background = Qt.green
    title = "Debug Print"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeDebugContent())


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

    def clear_output(self, index):
        return


@NodesRegister.register_class
class NodeInput(Node):
    title_background = Qt.blue
    title = 'Input Text'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeInputContent())
