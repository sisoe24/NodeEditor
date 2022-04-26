import contextlib

from PySide2.QtGui import QPainterPath
from PySide2.QtWidgets import QUndoCommand, QGraphicsScene


from src.widgets.node_edge import NodeEdge, NodeEdgeGraphics
from src.nodes import (
    NodesRegister, create_node, connect_output_edges, connect_input_edges
)


def graph_node(node):
    return NodesRegister.get_node_from_graph(node)


class MoveNodeCommand(QUndoCommand):
    def __init__(self, nodes, previous_position, description):
        super().__init__(description)

        self.nodes = nodes
        self.previous_position = previous_position

    def undo(self):
        for node, pos in self.previous_position.items():
            node = graph_node(node)
            node.setPos(pos)

    def redo(self):
        for node, pos in self.nodes.items():
            node = graph_node(node)
            node.setPos(pos)


class SelectCommand(QUndoCommand):
    def __init__(self, scene, previous_selection, current_selection, description):
        super().__init__(description)
        self.scene = scene
        self.previous_selection = previous_selection
        self.current_selection = current_selection

    def _set_selection(self, selection):
        self.scene.clearSelection()

        with contextlib.suppress(AttributeError):
            selection.setSelected(True)

    def undo(self):
        self._set_selection(self.previous_selection)

    def redo(self):
        self._set_selection(self.current_selection)


class BoxSelectCommand(QUndoCommand):
    def __init__(self, scene, previous_selection, current_selection, description):
        super().__init__(description)
        self.scene = scene
        self.previous_selection = previous_selection
        self.current_selection = current_selection

    def _set_selection(self, selection):
        if not selection:
            selection = QPainterPath()
        self.scene.setSelectionArea(selection)

    def undo(self):
        self._set_selection(self.previous_selection)

    def redo(self):
        self._set_selection(self.current_selection)


class ConnectEdgeCommand(QUndoCommand):
    def __init__(self, scene, start_socket, end_socket, description):
        super().__init__(description)

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket

    def undo(self):
        self.end_socket.remove_edge()

    def redo(self):
        NodeEdge(self.scene, self.start_socket, self.end_socket)


class DisconnectEdgeCommand(QUndoCommand):
    def __init__(self, scene, start_socket, end_socket, description):
        super().__init__(description)

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.edge = None

    def undo(self):
        NodeEdge(self.scene, self.start_socket, self.end_socket)

    def redo(self):
        pass


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
        self.node.node_graphics.setSelected(True)
        self.node.node_graphics.setZValue(1)


class DeleteNodeCommand(QUndoCommand):
    def __init__(self, scene, selected_nodes: list, description: str):
        super().__init__(description)

        self.scene = scene
        self.selected_nodes = selected_nodes

        self.nodes_data = {}
        self.input_edges = {}
        self.output_edges = {}

    def _create_nodes(self):
        for old_node in self.selected_nodes:
            node_data = self.nodes_data[old_node.node_id]

            node = create_node(self.scene, old_node.node_class)
            node.node_graphics.setPos(node_data['position']['x'],
                                      node_data['position']['y'])

            node_id = node.node_graphics.node_id
            self.input_edges[node_id] = node_data.get('input_edges', {})
            self.output_edges[node_id] = node_data.get('output_edges', {})

    def undo(self):
        def connected_edges(node_list):
            return bool([_ for _ in node_list.values() if _])

        self._create_nodes()

        if connected_edges(self.input_edges):
            connect_input_edges(self.scene, self.input_edges)

        if connected_edges(self.output_edges):
            connect_output_edges(self.scene, self.output_edges)

    def redo(self):
        """Append the node data into a class attribute and delete them."""
        for node in self.selected_nodes:

            node = graph_node(node)
            self.nodes_data[node.node_id] = node.data()

            node.delete_node()


class DeleteEdgeCommand(QUndoCommand):
    def __init__(self, edge: 'NodeEdgeGraphics', scene: 'QGraphicsScene', description: str):
        super().__init__(description)
        self.edge = edge.base
        self.scene = scene
        self._edge = None

    def undo(self):
        start_socket = self.edge.start_socket
        end_socket = self.edge.end_socket
        self._edge = NodeEdge(self.scene, start_socket, end_socket)

    def redo(self):
        if not self._edge:
            self.edge.delete_edge()
        else:
            self._edge.end_socket.remove_edge()
