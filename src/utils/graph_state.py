import json
from pprint import pformat, pprint

from PySide2.QtCore import QRectF, QRect
from PySide2.QtWidgets import (
    QGraphicsScene
)

from src.nodes import (
    connect_output_edges,
    extract_output_edges,
    create_node,
    NodesRegister,
)

from src.widgets.node_edge import NodeEdge
from src.widgets.node_graphics import NodeGraphics


def create_nodes_from_save_file(scene, file_data) -> dict:

    connections = {}
    for node_attrs in file_data['nodes'].values():

        node = create_node(scene, node_attrs['class'])
        node.set_position(node_attrs['position']['x'],
                          node_attrs['position']['y'])
        node.content.restore_state(node_attrs.get('content'))

        node_id = node.node_graphics.node_id
        connections[node_id] = node_attrs.get('output_edges', {})

    return connections


def load_scene(scene: 'QGraphicsScene', data: dict) -> None:
    scene.set_view_center(data['viewport']['x'], data['viewport']['y'])
    nodes = create_nodes_from_save_file(scene, data)
    connect_output_edges(scene, nodes)


def load_file(scene: 'QGraphicsScene', file: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        try:
            load_scene(scene, json.load(f))
        except Exception as err:
            print('Could not load the file.', err)


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

        # convert edge obj to str for json serialization
        edges = {str(i): v for i, v in extract_output_edges(node).items()}

        state['nodes'][node_data.get('id')] = {
            'class': node_data.get('class'),
            'position': node_data.get('position'),
            'output_edges': edges,
            'content': node.content.save_state()
        }

    return state


def save_file(scene, file):
    """Save current graph scene."""
    try:
        scene = scene_state(scene)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(scene, f, indent=2, sort_keys=True)
    except Exception as err:
        print('Could not save file: ', err)
