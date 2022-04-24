import os
import sys
import logging

from PySide2.QtCore import QRect, Qt
from PySide2.QtGui import QFont

from PySide2.QtWidgets import (
    QPushButton,
    QPlainTextEdit,
    QTabWidget,
    QMenu,
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
from src.utils.graph_state import load_file, save_file
from src.widgets.editor_menubar import NodeMenubar


from src.widgets.editor_scene import Scene
from src.widgets.node_edge import NodeEdge
from src.widgets.editor_view import GraphicsView
from src.widgets.node_graphics import create_node

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


class DebugWidget(QWidget):
    def __init__(self, node_editor, undo_stack):
        super().__init__()

        self.node_editor = node_editor
        self.scene = self.node_editor.scene.graphics_scene
        self.undo_stack = undo_stack

        self.tabs = QTabWidget()
        self.console = QPlainTextEdit()
        self.console.setFont(QFont('Menlo', 16))
        self.tabs.addTab(QUndoView(self.undo_stack), 'Undo History')
        self.tabs.addTab(self.console, 'Debug Console')

        self._btn_debug = QPushButton('Test')

        _layout = QVBoxLayout()
        _layout.addWidget(self.node_editor)
        _layout.addWidget(self._btn_debug)
        _layout.addWidget(self.tabs)

        self.setLayout(_layout)
        self._debug_add_nodes()

    def _write_to_console(self, text):
        self.tabs.setCurrentIndex(1)
        self.console.setPlainText(text)

    def _debug_add_nodes(self):

        node_test = create_node(self.scene, 'NodeTest')
        node_test.set_position(-150, 150)

        # node_debug = create_node(self.scene, 'NodeDebug')
        # node_debug.set_position(40, -40)

        node_example = create_node(self.scene, 'NodeExample')
        node_example.set_position(50, 0)

        # create debug edge
        start_socket_a = node_test.output_sockets[0]
        end_socket_a = node_example.input_sockets[0]
        NodeEdge(self.scene, start_socket_a.socket_graphics,
                 end_socket_a.socket_graphics)
        return

        start_socket_a = node_test.output_sockets[0]
        end_socket_a = node_example.input_sockets[1]
        # NodeEdge(start_socket_a.socket_graphics, end_socket_a.socket_graphics)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeEditor")
        self.setGeometry(-1077.296875, -5.31640625, 1080, 1980)

        self.undo_stack = QUndoStack(self)

        self.mouse_position = QLabel('')
        self.node_editor = NodeEditor(self)
        self.node_editor.view.mouse_position.connect(self.set_coords)

        debug_widget = DebugWidget(self.node_editor, self.undo_stack)
        debug_widget._btn_debug.clicked.connect(self._debug_function)
        self.setCentralWidget(debug_widget)

        self._scene = self.node_editor.scene.graphics_scene

        self._view = self.node_editor.view
        self._view.graph_debug.connect(debug_widget._write_to_console)

        self.menubar = NodeMenubar(self)
        self.setMenuBar(self.menubar)

        self._set_toolbar()
        self._set_status_bar()

        # save_file(self._scene, 'scripts/save_file.json')
        # self._load_file()

    def _load_file(self):
        file = 'scripts/save_file.json'
        load_file(self._scene, file)
        self.menubar._file_actions.editor_file = file
        self.setWindowTitle(os.path.basename(file))

    def _debug_function(self):
        """Debug function"""
        self._scene.clearSelection()

    def _set_toolbar(self):

        toolbar = QToolBar()
        toolbar.setStyleSheet('color: white;')

        self.file_action = QAction('File', self)
        self.file_action.setMenu(self.menubar.file_menu)
        toolbar.addAction(self.file_action)

        self.edit_action = QAction('Edit', self)
        self.edit_action.setMenu(self.menubar.edit_menu)
        toolbar.addAction(self.edit_action)

        self.add_action = QAction('Add', self)
        self.add_action.setMenu(self.menubar.add_menu)
        toolbar.addAction(self.add_action)

        self.addToolBar(toolbar)

    def set_coords(self, x, y):
        self.mouse_position.setText(f'{round(x)}, {round(y)}')

    def _set_status_bar(self):
        self.statusBar().addPermanentWidget(self.mouse_position)

    def show_status_message(self, msg, timeout=5000):
        self.statusBar().showMessage(msg, timeout)

    def contextMenuEvent(self, event):
        """Right click menu."""
        if event.modifiers() == Qt.ControlModifier:
            return

        menu = QMenu(self)
        menu.addMenu(self.menubar.file_menu)
        menu.addMenu(self.menubar.edit_menu)
        menu.addMenu(self.menubar.add_menu)
        menu.popup(event.globalPos())
        super().contextMenuEvent(event)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
