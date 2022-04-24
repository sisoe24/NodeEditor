import contextlib
from PySide2.QtGui import QPainterPath
from PySide2.QtCore import QMarginsF, Qt
from PySide2.QtWidgets import QUndoCommand

from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodesRegister, create_node


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
    # TODO: this class has much in common with the load method from graph_state.py
    # Should try to merge them.

    def __init__(self, nodes, scene, description):
        super().__init__(description)
        self.nodes = nodes
        self.scene = scene
        self.node_info = {}

    def _created_nodes(self):
        node_edges = {}

        for old_node in self.nodes:
            node_data = self.node_info[old_node._id]
            node = create_node(self.scene, old_node._class)
            node.node_graphics.setPos(node_data['position']['x'],
                                      node_data['position']['y'])
            node_edges[old_node._id] = node
        return node_edges

    @staticmethod
    def _create_input_edges(node, node_data):
        for edges in node_data['input_sockets'].values():
            for node_edges in edges.values():
                edge = node_edges['edges']

                if edge:
                    start_node = graph_node(edge.start_socket.node)
                    start_socket = start_node.base.output_sockets[edge.start_socket.index]

                    end_socket = node.input_sockets[edge.end_socket.index]

                    NodeEdge(start_socket.socket_graphics,
                             end_socket.socket_graphics)

    @staticmethod
    def _create_output_edges(node, node_data):
        for edges in node_data['output_sockets'].values():
            for node_edges in edges.values():
                edges = node_edges['edges']

                if not edges:
                    continue

                for edge in edges:
                    start_socket = node.output_sockets[edge.start_socket.index]

                    end_node = graph_node(edge.end_socket.node)
                    end_socket = end_node.base.input_sockets[edge.end_socket.index]

                    NodeEdge(start_socket.socket_graphics,
                             end_socket.socket_graphics)

    def undo(self):
        # FIXME: refactor
        node_edges = self._created_nodes()

        for node in node_edges.values():
            node_data = self.node_info[node.node_graphics._id]
            self._create_output_edges(node, node_data)
            self._create_input_edges(node, node_data)

    def redo(self):
        for node in self.nodes:
            self.node_info.update({node._id: node.info()})
            node = graph_node(node)
            node.delete_node()


class DeleteEdgeCommand(QUndoCommand):
    def __init__(self, edge, scene, description):
        super().__init__(description)
        self.edge = edge
        self.scene = scene
        self._edge = None

    def undo(self):
        start_socket = self.edge.edge.start_socket
        end_socket = self.edge.edge.end_socket
        self._edge = NodeEdge(self.scene, start_socket, end_socket)

    def redo(self):
        if not self._edge:
            self.edge.delete_edge()
        else:
            self._edge.end_socket.remove_edge()
