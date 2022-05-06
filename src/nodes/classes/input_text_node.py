
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node
from src.sockets import SocketInputType, SocketOutputType


class NodeInputContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_box = QPlainTextEdit('foo BAR')

        self.add_output(SocketOutputType.text, 'Text', pos=0)
        self.add_output(SocketOutputType.number, 'Text Length', pos=1)

        self.add_widget(self.text_box, pos=2)

    def get_output(self, index=1):

        if index == 0:
            return self.text_box.toPlainText()

        if index == 1:
            return str(len(self.text_box.toPlainText()))

        return ""

    def clear_output(self, index):
        return


@NodesRegister.register_class
class NodeInput(Node):
    title_background = Qt.blue
    title = 'Input Text'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeInputContent())
