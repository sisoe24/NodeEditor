import json
from pprint import pprint

from src.examples import nodes
from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodeGraphics


def _create_nodes(scene, file_data):

    node_edges = {}
    for node_type, node_attrs in file_data.items():

        # Review: is there a better way?
        create_node = getattr(nodes, node_attrs['class'])

        node = create_node(scene)
        node.set_position(node_attrs['position']['x'],
                          node_attrs['position']['y'])
        node_edges[node_type] = {'obj': node,
                                 'edges': node_attrs.get('output_edges', {})}

    return node_edges


def _extract_end_socket(node_edges, edge):
    end_connection = edge['end_socket']
    end_socket_obj = node_edges[end_connection['node']]['obj']
    return end_socket_obj.input_sockets[end_connection['index']]


def load_file(self):
    with open('save_file.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    node_edges = _create_nodes(self.node_editor.scene, data)

    for connections in node_edges.values():
        obj = connections['obj']

        for edge in connections['edges'].values():

            start_socket = obj.output_sockets[edge['start_socket_index']]
            end_socket = _extract_end_socket(node_edges, edge)

            NodeEdge(self.node_editor.view,
                     start_socket.socket_graphics,
                     end_socket.socket_graphics)


def _extract_output_edges(node: NodeGraphics):
    output_edges = {}
    index = 0

    for output_socket in node.node.output_sockets:
        socket = output_socket.socket_graphics

        if socket.has_edge():
            for edge in socket.edges:
                output_edges[f'edge.{index}'] = {
                    'start_socket_index': edge.start_socket.index,
                    'end_socket': {
                        'node': edge.end_socket.node.id(),
                        'index': edge.end_socket.index
                    }}

                index += 1
    return output_edges


def save_file(scene):
    """Save current graph scene."""
    graph_state = {}

    graph_nodes = [n for n in scene.items() if isinstance(n, NodeGraphics)]
    for node in graph_nodes:

        node_data = node.info()
        graph_state[node_data.get('id')] = {
            'class': node_data.get('class'),
            'position': node_data.get('position'),
            'output_edges': _extract_output_edges(node)
        }

    with open('save_file.json', 'w', encoding='utf-8') as file:
        json.dump(graph_state, file, indent=2)
