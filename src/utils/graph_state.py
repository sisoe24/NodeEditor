import json
from pprint import pprint

from PySide2.QtCore import QRectF, QRect, Qt
from PySide2.QtWidgets import (
    QGraphicsScene
)

from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodeGraphics, NodesRegister, create_node


def create_nodes_from_save_file(scene, file_data) -> dict:

    connections = {}
    for node_attrs in file_data['nodes'].values():

        node = create_node(scene, node_attrs['class'])
        node.set_position(node_attrs['position']['x'],
                          node_attrs['position']['y'])
        connections[node] = node_attrs.get('output_edges', {})

    return connections


def connect_output_edges(scene: 'QGraphicsScene', connections: dict) -> None:
    for node, edges in connections.items():
        for edge in edges.values():
            start_socket = node.output_sockets[edge['start_socket_index']]

            end_connection = edge['end_socket']
            end_node_id = end_connection['node']
            end_node = NodesRegister.get_node_from_id(end_node_id)
            end_socket = end_node.base.input_sockets[end_connection['index']]

            NodeEdge(scene, start_socket, end_socket)


def load_scene(scene: 'QGraphicsScene', data: dict) -> None:
    scene.clear()
    scene.set_view_center(data['viewport']['x'], data['viewport']['y'])
    connect_output_edges(scene, create_nodes_from_save_file(scene, data))


def load_file(scene: 'QGraphicsScene', file: str) -> None:
    NodesRegister.clean_register()
    with open(file, 'r', encoding='utf-8') as f:
        load_scene(scene, json.load(f))


def _extract_output_edges(node: NodeGraphics):
    output_edges = {}
    index = 0

    for output_socket in node.base.output_sockets:
        socket = output_socket

        if socket.has_edge():
            for edge in socket.edges:
                output_edges[f'edge.{index}'] = {
                    'start_socket_index': edge.start_socket.index,
                    'end_socket': {
                        'node': edge.end_socket.node._id,
                        'index': edge.end_socket.index
                    }}

                index += 1
    return output_edges


def _visible_viewport(scene):
    """Get the center of the viewport visible area."""
    view = scene.views()[0]
    scene_view = view.viewport()
    viewport = QRect(0, 0, scene_view.width(), scene_view.height())
    viewport_rect: QRectF = view.mapToScene(viewport).boundingRect().center()
    return {
        'x': viewport_rect.x(), 'y': viewport_rect.y(),
    }


def scene_state(scene) -> dict:
    """Generate the graph state."""
    state = {
        'viewport': _visible_viewport(scene),
        'nodes': {}
    }

    graph_nodes = [n for n in scene.items() if isinstance(n, NodeGraphics)]
    for node in graph_nodes:
        node_data = node.data()
        state['nodes'][node_data.get('id')] = {
            'class': node_data.get('class'),
            'position': node_data.get('position'),
            'output_edges': _extract_output_edges(node)
        }

    return state


def save_file(scene, file):
    """Save current graph scene."""
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(scene_state(scene), f, indent=2)
