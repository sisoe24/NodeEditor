"""Startup template for a Node object."""
from PySide2.QtCore import Qt

from PySide2.QtWidgets import (
    QDoubleSpinBox
)

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_socket import SocketType
from src.widgets.node_graphics import Node


class NodeNumberContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, node, parent=None):
        super().__init__(node, parent)

        self.add_input(SocketType.number, 'Number', pos=0)
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setValue(21.44)
        self.add_widget(self.spinbox, pos=1)
        self.add_output(SocketType.number, 'Number', pos=2)

    def restore_state(self, content):
        return self.spinbox.setValue(content.get('spinbox', 0.0))

    def save_state(self):
        return {"spinbox": self.spinbox.value()}

    def set_input(self, value, index):
        return ""

    def get_output(self, index):
        return str(self.spinbox.value())

    def clear_output(self, index):
        return


@NodesRegister.register_class
class NodeNumber(Node):
    title_background = Qt.gray
    title = 'Numbers'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeNumberContent(self))
