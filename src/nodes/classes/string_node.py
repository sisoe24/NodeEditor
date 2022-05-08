
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QLineEdit,
    QRadioButton,

)

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_socket import SocketType
from src.widgets.node_graphics import Node


class NodeStringContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, node, parent=None):
        super().__init__(node, parent)

        self.add_output_execute('Execute', pos=0)
        self.add_output(SocketType.text, 'Text', pos=1)

        self.make_upper = QRadioButton('Make Uppercase')
        self.make_upper.setChecked(True)
        self.add_widget(self.make_upper, pos=2)

        self.make_lower = QRadioButton('Make Lowercase')
        self.add_widget(self.make_lower, pos=3)

        self.make_title = QRadioButton('Make Titlecase')
        self.add_widget(self.make_title, pos=4)

        self.text = QLineEdit()
        self.text.setObjectName('Text')
        self.text.setPlaceholderText('text')
        self.add_input_widget(self.text, pos=5)

        self.add_input_execute('Execute', pos=6)

        self.output_text = "STRINGMODE"

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

    def clear_output(self, index):
        self.output_text = None


@NodesRegister.register_class
class NodeString(Node):
    title_background = QColor('#FAB27C')
    title = "String mod"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeStringContent(self))
