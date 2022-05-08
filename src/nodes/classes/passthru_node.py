"""Startup template for a Node object."""
from PySide2.QtCore import Qt

from PySide2.QtWidgets import (
    QDoubleSpinBox
)

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_socket import SocketType
from src.widgets.node_graphics import Node


class NodePassthruContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, node, parent=None):
        super().__init__(node, parent)
        self.add_input(SocketType.text, 'Text')
        self.add_output(SocketType.text, 'Text')

        self.output = "Passthru"

    def set_input(self, value, index):
        self.output = value

    def get_output(self, index):
        return self.output

    def clear_output(self, index):
        return


@NodesRegister.register_class
class NodePassthru(Node):
    title_background = Qt.gray
    title = 'Passthru'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodePassthruContent(self))
