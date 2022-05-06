
from PySide2.QtCore import Qt

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class NodeExecuteContent(NodeContent):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_output_execute(pos=0)

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeExecute(Node):
    title_background = Qt.red
    title = "Execute"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeExecuteContent())