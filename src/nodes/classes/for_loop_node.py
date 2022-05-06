
from PySide2.QtGui import QColor

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class NodeForLoopContent(NodeContent):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_output_execute(pos=0)
        self.add_input_execute(pos=1)
        self.add_input_list('List', pos=2)

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeForLoop(Node):
    title_background = QColor('#18B2A5')
    title = "For Loop"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeForLoopContent())
