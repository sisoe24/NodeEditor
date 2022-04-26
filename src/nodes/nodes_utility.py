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
            start_socket = node.output_sockets[edge['start_socket_index']]

            end_connection = edge['end_socket']
            end_node_id = end_connection['node']
            end_node = NodesRegister.get_node_from_id(end_node_id)
            end_socket = end_node.base.input_sockets[end_connection['index']]

            NodeEdge(scene, start_socket, end_socket)


def extract_output_edges(node):
    output_edges = {}
    index = 0

    for output_socket in node.base.output_sockets:
        socket = output_socket

        if socket.has_edge():
            for edge in socket.edges:
                output_edges[f'edge.{index}'] = {
                    'start_socket_index': edge.start_socket.index,
                    'end_socket': {
                        'node': edge.end_socket.node.node_id,
                        'index': edge.end_socket.index
                    }}

                index += 1
    return output_edges
