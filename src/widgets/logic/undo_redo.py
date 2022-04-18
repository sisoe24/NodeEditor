import json
from pprint import pformat
from PySide2.QtWidgets import QUndoCommand
from PySide2.QtGui import QPainterPath

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

    def graph_node(self):
        return NodesRegister.get_node_from_graph(self.node)

    def undo(self):
        node = self.graph_node()
        node.setPos(self.previous_position)

    def redo(self):
        node = self.graph_node()
        node.setPos(self.node_pos)


class SelectCommand(QUndoCommand):
    def __init__(self, scene, previous_selection, current_selection, description):
        super().__init__(description)
        self.scene = scene
        self.previous_selection = previous_selection
        self.current_selection = current_selection

    def selection_area(self, node):
        path = QPainterPath()
        path.addPolygon(node.mapToScene(node.boundingRect()))
        return path

    def undo(self):
        selection = self.previous_selection
        selection = self.selection_area(
            selection) if selection else QPainterPath()
        self.scene.setSelectionArea(selection)

    def redo(self):
        self.scene.setSelectionArea(
            self.selection_area(self.current_selection))


class BoxSelectCommand(QUndoCommand):
    def __init__(self, scene, description):
        super().__init__(description)

        self.scene = scene
        self.selection = self.scene.selectionArea()
        self.stack_previous = None

    def undo(self):
        print('box select undo')
        # print("➡ self.stack_previous :", self.stack_previous)
        self.scene.setSelectionArea(self.stack_previous)

    def redo(self):
        print('box select redo')
        self.stack_previous = self.selection
        # print("➡ self.selection :", self.selection)


class ConnectEdgeCommand(QUndoCommand):
    def __init__(self, start_socket, end_socket, description):
        super().__init__(description)
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.edge = None

    def undo(self):
        self.end_socket.remove_edge()

    def redo(self):
        self.edge = NodeEdge(self.start_socket, self.end_socket)


class DisconnectEdgeCommand(QUndoCommand):
    def __init__(self, start_socket, end_socket, description):
        super().__init__(description)

        self.start_socket = start_socket
        self.end_socket = end_socket

        self.edge = None

    def undo(self):
        self.edge = NodeEdge(self.start_socket, self.end_socket)

    def redo(self):
        pass
        # self.edge = NodeEdge(self.start_socket, self.end_socket)


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
        # FIXME: refactor
        node = create_node(self.scene, self.node._class)
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
    def __init__(self, edge, scene, description):
        super().__init__(description)
        self.edge = edge
        self.scene = scene
        self._edge = None

    def undo(self):
        start_socket = self.edge.edge.start_socket
        end_socket = self.edge.edge.end_socket
        self._edge = NodeEdge(start_socket, end_socket)

    def redo(self):
        if not self._edge:
            self.edge.delete_edge()
        else:
            self._edge.end_socket.remove_edge()


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
