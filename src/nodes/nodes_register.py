from pprint import pformat
from typing import Union


class NodesRegister:
    nodes = {}
    nodes_classes = {}
    all_nodes = []
    event_nodes = []

    @classmethod
    def register_class(cls, node_class):
        """Register a node class.

        This function is used as a wrapper on a node class declaration.
        """
        cls.nodes_classes[node_class.__name__] = node_class

        def wrapper(*args):
            return node_class(args[0])
        return wrapper

    @classmethod
    def clean_register(cls):
        """Clear the nodes in the register."""
        cls.nodes.clear()
        cls.all_nodes.clear()
        cls.event_nodes.clear()

    @classmethod
    def get_node_class_object(cls, node: str):
        """Get a class reference object.

        `NodeRegister.get_node_class_object('NodeExample')`.

        Returns:
            obj - The object reference for the node.

        Raises:
            RunTimeError: If the class is invalid.
        """
        node_class = cls.nodes_classes.get(node)
        if node_class:
            return node_class

        raise RuntimeError(f'Node class not found: {node}')

    @classmethod
    def get_node_from_graph(cls, node: 'NodeGraphics'):
        """Get a node from the graph by the class id.

        `NodeRegister.get_node_from_graph(node_graphics_obj)`

        Returns:
            (NodeGraphics) - A NodeGraphics object.
        """
        return cls.nodes[node.node_class].get(node.node_id)

    @classmethod
    def get_node_from_id(cls, _id: str) -> Union['NodeGraphics', None]:
        """Get a node from the graph by its id.

        `NodeRegister.get_node_from_id('NodeExample.001')`

        Returns:
            (NodeGraphics) - A NodeGraphics object if id was found, `None`
            otherwise.

        """
        for node in cls.nodes.values():
            for node_id in node:
                if node_id == _id:
                    return node[node_id]
        return None

    @classmethod
    def get_last_node_id(cls, node_class: str) -> str:
        """Get the last node id of a specific class from the graph.

        `NodeRegister.get_node_from_graph('NodeExample')`

        Returns:
            (str) - A node id e.g., `NodeExample.002`.
        """
        # XXX: maybe should return the object directly?
        return max(cls.nodes[node_class])

    @classmethod
    def reset_nodes_execution(cls) -> str:
        for node in cls.all_nodes:
            node.base.was_execute = False

    @classmethod
    def get_event_nodes(cls) -> str:
        return cls.event_nodes

    @classmethod
    def get_root_nodes(cls) -> str:
        """Get all of the root nodes in the graphs.

        `NodeRegister.ger_root_nodes()`

        Root nodes are nodes which have no parent node attached.

        Returns:
            (list) - A list of nodes.
        """
        starting_nodes = []
        for node in cls.all_nodes:
            node_data = node.data()
            if not node_data['parents'] and node_data['children']:
                starting_nodes.append(node.base)
        return starting_nodes

    @classmethod
    def register_node(cls, node: 'NodeGraphics') -> str:
        """Add a node to the current scene register.

        Returns:
            (str) - The id of the registered node.
        """
        cls.all_nodes.append(node)

        if node.base.is_event_node:
            cls.event_nodes.append(node)

        node_class = node.node_class
        node_data = cls.nodes.get(node_class)

        node_num = 1
        if node_data:
            for index, key in enumerate(sorted(node_data.keys()), 1):
                num = key.split('.')[-1]
                if index != int(num):
                    node_num = index
                    break
                node_num += 1
        else:
            cls.nodes.update({node_class: {}})

        node_id = f'{node_class}.{str(node_num).zfill(3)}'
        cls.nodes[node_class].update(({node_id: node}))

        return node_id

    @classmethod
    def unregister_node(cls, node: 'NodeGraphics') -> None:
        """Remove a node from the current scene register."""
        cls.all_nodes.remove(node)
        cls.nodes[node.node_class].pop(node.node_id)
