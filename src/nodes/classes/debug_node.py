
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QPlainTextEdit


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node
from src.widgets.node_socket import SocketType


class NodeDebugContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, node, parent=None):
        super().__init__(node, parent)

        self.add_output_execute(pos=0)
        self.add_input_execute(pos=1)
        self.text_box = QPlainTextEdit()
        self.add_input(SocketType.text, 'Text', pos=2)
        self.add_widget(self.text_box, pos=3)

    def set_input(self, value, index):
        self.text_box.setPlainText(str(value))

    def clear_output(self, index):
        return

    def get_output(self, index):
        return


@NodesRegister.register_class
class NodeDebug(Node):
    title_background = QColor('#21B24F')
    title = "Debug Print"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeDebugContent(self))
