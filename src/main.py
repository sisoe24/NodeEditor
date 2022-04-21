import sys
import json
import random
import logging

from PySide2.QtGui import (
    QKeySequence
)

from PySide2.QtWidgets import (
    QPushButton,
    QUndoView,
    QUndoStack,
    QAction,
    QToolBar,
    QLabel,
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
)
from src.widgets.editor_menubar import NodeMenubar


from src.widgets.editor_scene import Scene
from src.widgets.editor_view import GraphicsView
from src.widgets.node_edge import NodeEdge
from src.widgets.logic.undo_redo import (
    AddNodeCommand, LoadCommand, SaveCommand
)

from src.examples.nodes import *

LOGGER = logging.getLogger('nodeeditor.main')


class NodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.undo_stack = QUndoStack()

        # Create a graphic scene
        self.scene = Scene()

        # Create a graphic view
        self.view = GraphicsView(self.scene.graphics_scene, self)

        _layout = QVBoxLayout()
        _layout.setSpacing(5)
        _layout.addWidget(self.view)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(_layout)

        self._debug_add_nodes()

    def _debug_add_nodes(self):

        return
        node_test = nodes.NodeDebug(self.scene.graphics_scene)
        node_test.set_position(-200, 0)

        # node_debug = nodes.NodeDebug(self.scene.graphics_scene)
        # node_debug.set_position(40, -40)

        node_example = nodes.NodeExample(self.scene.graphics_scene)
        node_example.set_position(40, -40)

        # create debug edge
        start_socket_a = node_test.output_sockets[0]
        end_socket_a = node_example.input_sockets[0]
        NodeEdge(start_socket_a.socket_graphics, end_socket_a.socket_graphics)

        start_socket_a = node_test.output_sockets[0]
        end_socket_a = node_example.input_sockets[1]
        # NodeEdge(start_socket_a.socket_graphics, end_socket_a.socket_graphics)


class DebugWidget(QWidget):
    def __init__(self, node_editor, undo_stack):
        super().__init__()

        self.node_editor = node_editor
        self.scene = self.node_editor.scene.graphics_scene
        self.undo_stack = undo_stack

        btn = QPushButton('Add Node Example')
        btn.clicked.connect(lambda: self.add_node(nodes.NodeExample))

        btn1 = QPushButton('Add Node Debug')
        btn1.clicked.connect(lambda: self.add_node(nodes.NodeDebug))

        _layout = QVBoxLayout()

        _layout.addWidget(self.node_editor)
        _layout.addWidget(btn)
        _layout.addWidget(btn1)
        _layout.addWidget(QUndoView(self.undo_stack))

        self.setLayout(_layout)

    def add_node(self, node):
        n1 = random.randint(-300, 300)
        n2 = random.randint(-300, 300)
        command = AddNodeCommand(self.scene, (0, 0), node, 'Add Node')
        self.undo_stack.push(command)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeEditor")
        self.setGeometry(-1077.296875, -5.31640625, 1080, 1980)

        self.undo_stack = QUndoStack(self)

        self.mouse_position = QLabel('')
        self.node_editor = NodeEditor(self)
        self.node_editor.view.mouse_position.connect(self.set_coords)

        widget = DebugWidget(self.node_editor, self.undo_stack)
        self.setCentralWidget(widget)

        self._scene = self.node_editor.scene.graphics_scene
        self._add_actions()
        self.set_status_bar()

        # load_file(self._scene)
        # save_file(self._scene)
        self.setMenuBar(NodeMenubar(self))

    def _add_actions(self):

        toolbar = QToolBar()
        toolbar.setStyleSheet('color: white;')

        self.addToolBar(toolbar)

    def set_coords(self, x, y):
        self.mouse_position.setText(f'{round(x)}, {round(y)}')

    def set_status_bar(self):
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.mouse_position)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
