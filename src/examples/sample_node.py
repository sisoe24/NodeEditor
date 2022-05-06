"""Startup template for a Node object."""
from PySide2.QtCore import Qt


from src.nodes import NodeContent, NodesRegister
from src.widgets.node_graphics import Node


class __NODECLASS__Content(NodeContent):
    """The node content widgets container class."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_input(self, value, index):
        return ""

    def get_output(self, index):
        return ""

    def clear_output(self, index):
        return


@NodesRegister.register_class
class __NODECLASS__(Node):
    title_background = Qt.gray
    title = '__NODETITLE__'

    def __init__(self, scene):
        super().__init__(scene=scene, node=self, content=__NODECLASS__Content())
