import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QComboBox,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit
)


from ..widgets.node_graphics import Node, NodeContent
LOGGER = logging.getLogger('nodeeditor.node_input')


class NodeInputContent(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['foo', 'bar'])

        # self.add_widget(self.combo_box)
        self.add_output('Output 1')
        self.add_output('Output 2')
        self.add_input(QLabel('Input 1'))


class NodeInput(Node):
    title_background = Qt.red
    title = "Input Node"

    def __init__(self, scene):
        self.node_content = NodeInputContent()
        super().__init__(scene=scene, node=self, content=self.node_content)

    @property
    def layout_size(self):
        return self.node_content._layout.sizeHint()
