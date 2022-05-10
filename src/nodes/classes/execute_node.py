
from PySide2.QtGui import QColor

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_socket import SocketType
from src.widgets.node_graphics import Node


class NodeExecuteContent(NodeContent):
    def __init__(self, node, parent=None):
        super().__init__(node, parent)

        self.add_output_execute(pos=0)

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeExecute(Node):
    title_background = QColor('#EE0000')
    title = "Event"
    is_event_node = True

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeExecuteContent(self))
