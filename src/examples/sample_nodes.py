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
