import os
import sys
import json
import logging
from pprint import pprint

from PySide2.QtCore import (
    QSettings,
    QCoreApplication
)
from PySide2.QtWidgets import (
    QGraphicsScene,
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
from src.widgets.node_graphics import NodeGraphics

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

        node_example = nodes.NodeExample(self.scene)
        node_example.set_position(-75, 0)

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

        self._add_actions()

        self.setCentralWidget(self.node_editor)
        self.set_status_bar()

        self.load_file()
        # self.save_file()

    def save_file(self):
        scene: QGraphicsScene = self.node_editor.scene.graphics_scene

        nodes = [x for x in scene.items() if isinstance(x, NodeGraphics)]

        graph_state = {'nodes': []}
        for item in nodes:

            edges = {}
            index = 0

            for input_socket in item.node.output_sockets:
                socket = input_socket.socket_graphics
                if socket.has_edge():
                    for edge in socket.edges:
                        edges[f'edge.{index}'] = {
                            'start_socket': edge.start_point.index,
                            'end_socket': {
                                'node': edge.end_point.node.node.id(),
                                'socket': edge.end_point.index
                            }}
                        index += 1

            graph_state['nodes'].append(
                {item.node.id(): {
                    'class': f'{item.node}',
                    'position': {'x': item.pos().x(), 'y': item.pos().y()},
                    'edges': edges
                }})

        with open('save_file.json', 'w', encoding='utf-8') as file:
            json.dump(graph_state, file, indent=2)

    def load_file(self):
        # TODO: extract into own module/class

        with open('save_file.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        node_edges = {}

        for node_objects in data['nodes']:
            for node_type, node_attributes in node_objects.items():

                # Review: is there a better way?
                create_node = getattr(nodes, node_attributes['class'])

                node = create_node(self.node_editor.scene)
                node.set_position(node_attributes['position']['x'],
                                  node_attributes['position']['y'])

                edges = node_attributes.get('edges', {})
                node_edges[node_type] = {'obj': node, 'edges': edges}

        for node, connections in node_edges.items():
            obj = connections['obj']
            for edge in connections['edges'].values():
                start_socket = obj.output_sockets[edge['start_socket']]

                end_edge = edge['end_socket']
                end_node = end_edge.get('node')
                end_socket_obj = node_edges.get(end_node).get('obj')
                end_socket = end_socket_obj.input_sockets[end_edge['socket']]

                NodeEdge(self.node_editor.view,
                         start_socket.socket_graphics,
                         end_socket.socket_graphics)

    def _add_actions(self):
        save = QAction('Save File', self)
        save.triggered.connect(self.save_file)

        load = QAction('Load File', self)
        load.triggered.connect(self.load_file)

        toolbar = QToolBar()
        toolbar.setStyleSheet('color: white;')
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
