
from PySide2.QtGui import QColor

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class NodeConditionalsContent(NodeContent):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_input_execute('Execute', 2)

        self.condition = self.add_input_boolean('Condition', pos=3)

        self.add_output_execute('True', 0)
        self.add_output_execute('False', 1)

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeConditionals(Node):
    title_background = QColor('#BD74D3')
    title = "If/Else"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeConditionalsContent())
