import json

from src.examples import nodes
from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodeGraphics


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


def save_file(scene):
    """Save current graph scene."""
    # Review: I might not need a key 'nodes'
    graph_state = {'nodes': []}

    graph_nodes = [n for n in scene.items() if isinstance(n, NodeGraphics)]

    for node in graph_nodes:

        output_edges = {}
        index = 0

        for output_socket in node.node.output_sockets:
            socket = output_socket.socket_graphics

            if socket.has_edge():

                for edge in socket.edges:

                    output_edges[f'edge.{index}'] = {
                        'start_socket': edge.start_socket.index,
                        'end_socket': {
                            'node': edge.end_socket.node.node.id(),
                            'socket': edge.end_socket.index
                        }}

                    index += 1

        graph_state['nodes'].append(
            {node.node.id(): {
                'class': f'{node.node}',
                'position': {'x': node.pos().x(), 'y': node.pos().y()},
                'output_edges': output_edges
            }})

    with open('save_file.json', 'w', encoding='utf-8') as file:
        json.dump(graph_state, file, indent=2)
