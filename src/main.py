import sys
import logging

from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QColor, QBrush, QPen
from PySide2.QtWidgets import (
    QLabel,
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QGraphicsItem
)


from src.widgets.editor_scene import Scene
from src.widgets.editor_view import GraphicsView
from src.nodes import node_input
from src.nodes import node_test

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
        node = node_test.NodeTest(self.scene)
        node.set_position(-450, -250)

        node1 = node_input.NodeInput(self.scene)
        node1.set_position(-70, -50)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("NodeEditor")
        self.setGeometry(-1077.296875, -5.31640625, 1080, 1980)

        self.mouse_position = QLabel('')
        self.node_editor = NodeEditor()
        self.node_editor.view.mouse_position.connect(
            self.mouse_position.setText)

        self.setCentralWidget(self.node_editor)
        self.set_status_bar()

    def set_status_bar(self):
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.mouse_position)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
