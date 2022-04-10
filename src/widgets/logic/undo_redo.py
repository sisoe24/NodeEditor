import json
from pprint import pformat
from PySide2.QtWidgets import QUndoCommand

from src.utils.graph_state import load_file, load_scene, save_file, scene_state
from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodesRegister, create_node


class MoveNodeCommand(QUndoCommand):
    def __init__(self, node, previous_position, description):
        super().__init__(description)
        self.node = node
        self.node_id = node._id

        self.node_pos = node.pos()
        self.previous_position = previous_position

    def undo(self):
        node = NodesRegister.get_node(self.node)
        node.setPos(self.previous_position)

    def redo(self):
        node = NodesRegister.get_node(self.node)
        node.setPos(self.node_pos)


class ConnectEdgeCommand(QUndoCommand):
    def __init__(self, start_socket, end_socket, description):
        super().__init__(description)
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.edge = None

    def undo(self):
        self.edge.edge_graphics.delete_edge()

    def redo(self):
        self.edge = NodeEdge(self.start_socket, self.end_socket)


class AddNodeCommand(QUndoCommand):
    def __init__(self, scene, pos, node, description):
        super().__init__(description)
        self._node = node
        self.scene = scene
        self.node_pos = pos
        self.node = None

    def undo(self):
        self.node.node_graphics.delete_node()

    def redo(self):
        self.node = self._node(self.scene)
        self.node.set_position(*self.node_pos)


class DeleteNodeCommand(QUndoCommand):
    def __init__(self, node, scene, description):
        super().__init__(description)
        self.node = node
        self.scene = scene
        self.node_info = None

    def undo(self):
        node_class = NodesRegister.nodes_types.get(self.node._class)
        node = node_class(self.scene)

        node.node_graphics.setPos(
            self.node_info['position']['x'],
            self.node_info['position']['y']
        )
        for edges in self.node_info['input_sockets'].values():
            for edge in edges.values():
                edge = edge['edges']
                if edge:
                    end_socket = node.input_sockets[edge.end_socket.index]
                    NodeEdge(edge.start_socket, end_socket.socket_graphics)

        for edges in self.node_info['output_sockets'].values():
            for edge in edges.values():
                edge = edge['edges']
                if edge:
                    for n in edge:
                        start_socket = node.output_sockets[n.start_socket.index]
                        NodeEdge(start_socket.socket_graphics, n.end_socket)

    def redo(self):
        self.node_info = self.node.info()
        self.node.delete_node()


class DeleteEdgeCommand(QUndoCommand):
    def __init__(self,  description):
        super().__init__(description)

    def undo(self):
        print('delete edge undo')

    def redo(self):
        print('delete edge redo')


class LoadCommand(QUndoCommand):
    def __init__(self, scene, description):
        super().__init__(description)
        self.scene = scene
        self.current_scene = scene_state(self.scene)

    def undo(self):
        self.scene.clear()
        load_scene(self.scene, self.current_scene)

    def redo(self):
        load_file(self.scene)


class SaveCommand(QUndoCommand):
    def __init__(self, scene, description):
        super().__init__(description)
        self.scene = scene

        with open('save_file.json', 'r', encoding='utf-8') as file:
            self.current_file = json.load(file)

    def undo(self):
        with open('save_file.json', 'w', encoding='utf-8') as file:
            json.dump(self.current_file, file)

        load_file(self.scene)

    def redo(self):
        save_file(self.scene)
