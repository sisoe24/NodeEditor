import json
from pprint import pprint

from PySide2.QtCore import QRectF, QRect, Qt

from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodeGraphics, create_node


def _create_nodes(scene, file_data):

    node_edges = {}
    for node_type, node_attrs in file_data['nodes'].items():

        node = create_node(scene, node_attrs['class'])
        node.set_position(node_attrs['position']['x'],
                          node_attrs['position']['y'])
        node_edges[node_type] = {'obj': node,
                                 'edges': node_attrs.get('output_edges', {})}

    return node_edges


def _extract_end_socket(node_edges, edge):
    end_connection = edge['end_socket']
    end_socket_obj = node_edges[end_connection['node']]['obj']
    return end_socket_obj.input_sockets[end_connection['index']]


def load_scene(scene, data):
    # center the view
    scene._set_view_center(data['viewport']['x'], data['viewport']['y'])

    scene.clear()
    node_edges = _create_nodes(scene, data)

    for connections in node_edges.values():
        obj = connections['obj']

        for edge in connections['edges'].values():
            start_socket = obj.output_sockets[edge['start_socket_index']]
            end_socket = _extract_end_socket(node_edges, edge)

            NodeEdge(scene, start_socket.socket_graphics,
                     end_socket.socket_graphics)


def load_file(scene, file):
    with open(file, 'r', encoding='utf-8') as f:
        load_scene(scene, json.load(f))


def _extract_output_edges(node: NodeGraphics):
    output_edges = {}
    index = 0

    for output_socket in node.base.output_sockets:
        socket = output_socket.socket_graphics

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
        node_data = node.info()
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
