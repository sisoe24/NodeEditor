import sys
import logging

from PySide2.QtWidgets import (
    QLabel,
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
)


from src.widgets.editor_scene import Scene
from src.widgets.editor_view import GraphicsView
from src.examples.nodes import *
from src.widgets.node_edge import NodeEdge

LOGGER = logging.getLogger('nodeeditor.main')


class NodeEditor(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # Create a graphic scene
        self.scene = Scene()

        # Create a graphic view
        self.view = GraphicsView(self.scene.graphics_scene)

        _layout = QVBoxLayout()
        _layout.setSpacing(5)
        _layout.addWidget(self.view)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(_layout)

        self._debug_add_nodes()

    def _debug_add_nodes(self):

        node_test = nodes.NodeExample3(self.scene)
        node_test.set_position(-245, 0)

        node_debug = nodes.NodeExample2(self.scene)
        node_debug.set_position(95, 0)

        node_example = nodes.NodeExample1(self.scene)
        node_example.set_position(-75, 0)
        return

        # create debug edge
        start_socket = node_example.output_sockets[0]
        end_socket = node_debug.input_sockets[0]

        NodeEdge(self.view, start_socket.socket_graphics,
                 end_socket.socket_graphics)

        start_socket = node_example.output_sockets[1]
        end_socket = node_debug.input_sockets[0]

        NodeEdge(self.view, start_socket.socket_graphics,
                 end_socket.socket_graphics)

        start_socket = node_example.output_sockets[2]
        end_socket = node_debug.input_sockets[1]

        NodeEdge(self.view, start_socket.socket_graphics,
                 end_socket.socket_graphics)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("NodeEditor")
        self.setGeometry(-1077.296875, -5.31640625, 1080, 1980)

        self.mouse_position = QLabel('')
        self.node_editor = NodeEditor()
        self.node_editor.view.mouse_position.connect(self.set_coords)

        self.setCentralWidget(self.node_editor)
        self.set_status_bar()

    def set_coords(self, x, y):
        self.mouse_position.setText(f'{round(x)}, {round(y)}')

    def set_status_bar(self):
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.mouse_position)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
