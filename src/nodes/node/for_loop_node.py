
from PySide2.QtCore import Qt

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class NodeForLoopContent(NodeContent):
    def __init__(self, parent=None):
        super().__init__(parent)

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeForLoop(Node):
    title_background = Qt.red
    title = "For Loop"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeForLoopContent())
