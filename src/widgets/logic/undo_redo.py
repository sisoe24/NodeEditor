import json
from PySide2.QtWidgets import QUndoCommand

from src.utils.graph_state import load_file, load_scene, save_file, scene_state


class MoveNodeCommand(QUndoCommand):
    def __init__(self, node, previous_position, description):
        super().__init__(description)
        self.node = node
        self.node_pos = self.node.pos()
        self.previous_position = previous_position

    def undo(self):
        self.node.setPos(self.previous_position)

    def redo(self):
        self.node.setPos(self.node_pos)


class ConnectEdgeCommand(QUndoCommand):
    def __init__(self, edge, description):
        super().__init__(description)
        self.edge = edge

    def undo(self):
        print('undo')

    def redo(self):
        print('redo')


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


class LoadCommand(QUndoCommand):
    def __init__(self, scene, description):
        super().__init__(description)
        self.scene = scene
        self.current_scene = scene_state(self.scene)

    def undo(self):
        self.scene.clear()
        load_scene(self.scene, self.current_scene)

    def redo(self):
        load_file(self.scene)


class SaveCommand(QUndoCommand):
    def __init__(self, scene, description):
        super().__init__(description)
        self.scene = scene

        with open('save_file.json', 'r', encoding='utf-8') as file:
            self.current_file = json.load(file)

    def undo(self):
        with open('save_file.json', 'w', encoding='utf-8') as file:
            json.dump(self.current_file, file)

        load_file(self.scene)

    def redo(self):
        save_file(self.scene)
