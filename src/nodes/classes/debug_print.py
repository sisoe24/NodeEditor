
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QPlainTextEdit


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node
from src.widgets.node_socket import SocketType


class NodeDebugContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_input_execute(label='Print', pos=0)
        self.text_box = QPlainTextEdit()
        self.add_input(SocketType.text, 'Text', pos=1)
        self.add_widget(self.text_box, pos=2)

    def set_input(self, value, index):
        super().set_input(value, index)
        self.text_box.setPlainText(value)

    def clear_output(self, index):
        return

    def get_output(self, index):
        return


@NodesRegister.register_class
class NodeDebug(Node):
    title_background = QColor('#21B24F')
    title = "Debug Print"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeDebugContent())
