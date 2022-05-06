"""Startup template for a Node object."""
from PySide2.QtCore import Qt


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class NodeNumberContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_input('input_number', 'Number', pos=0)
        self.add_output('output_number', 'Number', pos=1)

    def set_input(self, value, index):
        return ""

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return


@NodesRegister.register_class
class NodeNumber(Node):
    title_background = Qt.gray
    title = 'Increment number'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeNumberContent())
