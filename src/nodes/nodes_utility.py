from PySide2.QtWidgets import (
    QGraphicsScene
)

from src.nodes import NodesRegister
from src.widgets.node_edge import NodeEdge


def create_node(scene: QGraphicsScene, node_class: str) -> 'Node':
    """Create a node from a node class name.

    `create_node(scene, 'NodeTest') -> Node`
    """
    node = NodesRegister.get_node_class_object(node_class)
    return node(scene)


def connect_output_edges(scene: 'QGraphicsScene', connections: dict) -> None:
    for node, edges in connections.items():
        for edge in edges.values():

            new_node = NodesRegister.get_node_from_id(node).base
            start_socket = new_node.output_sockets[edge['start_socket']['index']]

            end_connection = edge['end_socket']
            end_node_id = end_connection['node']
            end_node = NodesRegister.get_node_from_id(end_node_id)
            end_socket = end_node.base.input_sockets[end_connection['index']]

            NodeEdge(scene, start_socket, end_socket)


def connect_input_edges(scene: 'QGraphicsScene', connections: dict) -> None:
    for node, edges in connections.items():
        for edge in edges.values():

            node = NodesRegister.get_node_from_id(node).base
            end_socket = node.input_sockets[edge['end_socket']['index']]

            start_connection = edge['start_socket']
            start_node_id = start_connection['node']
            start_node = NodesRegister.get_node_from_id(start_node_id)
            start_socket = start_node.base.output_sockets[start_connection['index']]

            NodeEdge(scene, start_socket, end_socket)


def _create_edge_connection_data(edges: dict, index: int, edge: NodeEdge):
    edges[f'edge.{index}'] = {
        'end_socket': {
            'node': edge.end_socket.node.node_id,
            'index': edge.end_socket.index
        },
        'start_socket': {
            'node': edge.start_socket.node.node_id,
            'index': edge.start_socket.index
        }}


def extract_output_edges(node) -> dict:
    """Extract the output edges from a node.

    Args:
        node (Node): The node object.

    Returns:
        (dict): A dictionary with all of the output edges data.
    """
    edges = {}
    index = 0
    for socket in node.base.output_sockets:
        if socket.has_edge():
            for edge in socket.edges:
                _create_edge_connection_data(edges, index, edge)
                index += 1
    return edges


def extract_input_edges(node) -> dict:
    """Extract the input edges from a node.

    Args:
        node (Node): The node object.

    Returns:
        (dict): A dictionary with all of the input edges data.
    """
    edges = {}
    index = 0
    for socket in node.base.input_sockets:
        if socket.has_edge():
            edge = socket.get_edges()
            _create_edge_connection_data(edges, index, edge)
            index += 1

    return edges
