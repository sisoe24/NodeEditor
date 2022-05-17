
from PySide2.QtGui import QColor

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node
from src.widgets.node_socket import SocketType


class NodeForLoopContent(NodeContent):
    def __init__(self, node, parent=None):
        super().__init__(node, parent)

        self.add_output_execute(pos=0)
        self.add_output(SocketType.value, 'Array element', pos=1)
        self.add_output(SocketType.number, 'Array index', pos=2)
        self.add_input_execute(pos=3)
        self.add_input_list('List', pos=4)

        self.output = ['virgil', 'sisoe', 'lara']

    def get_output(self, index):
        if index == 1:
            return self.output
        if index == 2:
            return range(len(self.output))

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeForLoop(Node):
    title_background = QColor('#18B2A5')
    title = "For Loop"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeForLoopContent(self))
