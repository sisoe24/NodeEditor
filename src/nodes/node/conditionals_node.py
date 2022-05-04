
from PySide2.QtWidgets import (
    QCheckBox
)

from PySide2.QtCore import Qt

from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class NodeConditionalsContent(NodeContent):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_input('Execute', 2)

        self.condition = QCheckBox('Condition')
        self.add_input_widget(self.condition, pos=3)

        self.add_output('True', 0)
        self.add_output('False', 1)

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return ""

    def set_input(self, value, index):
        return ""


@NodesRegister.register_class
class NodeConditionals(Node):
    title_background = Qt.red
    title = "If/Else"

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=NodeConditionalsContent())
