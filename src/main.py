import sys
import logging


from PySide2.QtWidgets import (
    QAction,
    QToolBar,
    QLabel,
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
)


from src.widgets.editor_scene import Scene
from src.widgets.editor_view import GraphicsView
from src.widgets.node_edge import NodeEdge

from src.utils.graph_state import load_file, save_file

from src.examples.nodes import *

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

        return
        node_test = nodes.NodeTest(self.scene)
        node_test.set_position(-245, 0)

        node_debug = nodes.NodeDebug(self.scene)
        node_debug.set_position(95, 0)

        # node_example = nodes.NodeExample(self.scene)
        # node_example.set_position(-75, 0)

        # create debug edge
        start_socket_b = node_test.output_sockets[1]
        start_socket_a = node_test.output_sockets[0]
        end_socket_a = node_debug.input_sockets[0]
        end_socket_b = node_debug.input_sockets[1]
        end_socket_c = node_debug.input_sockets[2]

        NodeEdge(self.view, start_socket_a.socket_graphics,
                 end_socket_a.socket_graphics)

        NodeEdge(self.view, start_socket_a.socket_graphics,
                 end_socket_b.socket_graphics)

        NodeEdge(self.view, start_socket_b.socket_graphics,
                 end_socket_c.socket_graphics)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("NodeEditor")
        self.setGeometry(-1077.296875, -5.31640625, 1080, 1980)

        self.mouse_position = QLabel('')
        self.node_editor = NodeEditor()
        self.node_editor.view.mouse_position.connect(self.set_coords)

        self.setCentralWidget(self.node_editor)

        self._scene = self.node_editor.scene.graphics_scene
        self._add_actions()
        self.set_status_bar()

        # load_file(self._scene)
        # save_file(self._scene)

    def _add_actions(self):
        new = QAction('New File', self)
        new.triggered.connect(self._scene.clear)

        save = QAction('Save File', self)
        save.triggered.connect(lambda: save_file(self._scene))

        load = QAction('Load File', self)
        load.triggered.connect(lambda: load_file(self._scene))

        toolbar = QToolBar()
        toolbar.setStyleSheet('color: white;')
        toolbar.addAction(new)
        toolbar.addAction(save)
        toolbar.addAction(load)
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
