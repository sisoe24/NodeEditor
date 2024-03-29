import os
from functools import partial

from PySide2.QtGui import (
    QKeySequence
)

from PySide2.QtWidgets import (
    QMessageBox,
    QFileDialog,
    QWidget,
    QAction,
    QMenuBar,
)

from src.nodes import NodesRegister
from src.widgets.logic.undo_redo import AddNodeCommand, DeleteNodeCommand
from src.utils.graph_state import connect_output_edges, load_file, save_file


class EditorActions(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.top_window = self.topLevelWidget()
        self.undo_stack = self.top_window.undo_stack
        self.scene = self.top_window._scene
        self.view = self.scene.views()[0]


class EditorFileActions(EditorActions):
    def __init__(self, parent):
        super().__init__(parent)

        self.editor_file = None

        self.new_file_act = QAction('New File', self)
        self.new_file_act.setShortcut(QKeySequence.New)
        self.new_file_act.triggered.connect(self.new_file)

        self.open_file_act = QAction('Open File...', self)
        self.open_file_act.setShortcut(QKeySequence.Open)
        self.open_file_act.triggered.connect(self.open_file)

        self.save_file_act = QAction('Save File', self)
        self.save_file_act.setShortcut(QKeySequence.Save)
        self.save_file_act.triggered.connect(self.save_file)

        self.save_file_as_act = QAction('Save File As...', self)
        self.save_file_as_act.setShortcut(QKeySequence.SaveAs)
        self.save_file_as_act.triggered.connect(self.save_file_as)

    def save_file(self):
        if self.editor_file:
            save_file(self.scene, self.editor_file)
            self.top_window.show_status_message('File Saved')
        else:
            self.save_file_as()

    def save_file_as(self):
        # TODO: make scripts path absolute
        file, _ = QFileDialog.getSaveFileName(caption='Save File as...',
                                              dir='scripts',
                                              filter='*.json')
        if file:
            save_file(self.scene, file)
            self.editor_file = file
            self.top_window.show_status_message('File Saved')
            self.top_window.setWindowTitle(os.path.basename(file))

    def _document_modified_dialog(self):
        dialog = QMessageBox()
        dialog.setText('The document has been modified.')
        dialog.setIcon(QMessageBox.Question)
        dialog.setInformativeText('Do you want to save your changes?')
        dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Discard |
                                  QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Save)
        return dialog.exec_()

    def _cancel_action(self):
        if not self.undo_stack.isClean():
            user_choice = self._document_modified_dialog()

            if user_choice == QMessageBox.Cancel:
                return True

            if user_choice == QMessageBox.Save:
                self.save_file_as()

        return False

    def new_file(self):
        if self._cancel_action():
            return
        self.top_window.reset_graph()
        self.top_window.show_status_message('New Graph')

    def open_file(self):
        if self._cancel_action():
            return

        # TODO: make scripts path absolute
        file, _ = QFileDialog.getOpenFileName(caption='Open File...',
                                              dir='scripts',
                                              filter='*.json')
        if file:
            self.top_window.reset_graph()
            load_file(self.scene, file)
            self.editor_file = file
            self.top_window.setWindowTitle(os.path.basename(file))
            self.top_window.show_status_message('File Loaded')


class EditorEditActions(EditorActions):
    def __init__(self, parent):
        super().__init__(parent)

        self.undo_act = self.undo_stack.createUndoAction(self, 'Undo')
        self.undo_act.setShortcut(QKeySequence.Undo)

        self.redo_act = self.undo_stack.createRedoAction(self, 'Redo')
        self.redo_act.setShortcut(QKeySequence.Redo)

        self.nodes_copy_stack = []

        self.duplicate_act = QAction('Duplicate', self)
        self.duplicate_act.setShortcut(QKeySequence('shift+D'))
        self.duplicate_act.triggered.connect(self.duplicate_nodes)

        self.copy_act = QAction('Copy', self)
        self.copy_act.setShortcut(QKeySequence.Copy)
        self.copy_act.triggered.connect(self.copy_nodes)

        self.paste_act = QAction('Paste', self)
        self.paste_act.setShortcut(QKeySequence.Paste)
        self.paste_act.triggered.connect(self.paste_nodes)

        self.delete_act = QAction('Delete', self)
        self.delete_act.setShortcut(QKeySequence.Delete)
        self.delete_act.triggered.connect(self.delete_nodes)

    def duplicate_nodes(self):
        self.nodes_copy_stack.clear()
        for node in self.view.selected_nodes():
            self.nodes_copy_stack.append(node)

        self.paste_nodes()

    def copy_nodes(self):
        self.nodes_copy_stack.clear()
        for item in self.view.selected_nodes():
            self.nodes_copy_stack.append(item)

    def _increment_node_reference(self, connections):
        # HACK: after copying a node, increment its reference id so to be able
        # to connect the edge to the newly copied version.
        for edges in connections.values():
            for edge in edges.values():

                node_id = edge['end_socket']['node']
                node_class, _ = node_id.split('.')
                node = NodesRegister.get_last_node_id(node_class)

                edge['end_socket']['node'] = node

    def paste_nodes(self):
        self.scene.clearSelection()

        connections = {}

        copy_stack_ids = [node.node_id for node in self.nodes_copy_stack]

        for node in self.nodes_copy_stack:

            node_info = node.data()
            x = node_info['position']['x']
            y = node_info['position']['y']

            node = NodesRegister.get_node_class_object(node_info['class'])
            command = AddNodeCommand(self.scene, (x, y), node, 'Add Node')
            self.undo_stack.push(command)

            output_edges = node_info['output_edges']

            for connection in output_edges.values():
                end_node = connection['end_socket']['node']

                if end_node in copy_stack_ids:
                    node_id = command.node.node_graphics.node_id
                    connections[node_id] = output_edges

        if not connections:
            return

        self._increment_node_reference(connections)
        connect_output_edges(self.scene, connections)

    def delete_nodes(self):
        nodes = self.view.selected_nodes()
        if nodes:
            command = DeleteNodeCommand(self.scene, nodes, 'Delete node')
            self.undo_stack.push(command)


class EditorAddActions(EditorActions):
    def __init__(self, parent):
        super().__init__(parent)

        self.nodes = []
        self.top_window = self.topLevelWidget()

        nodes = NodesRegister.nodes_classes.items()
        for node, obj in nodes:

            action = QAction(obj.title, self)

            # XXX: lambda does not work in this case, don't know why
            # err: Cell variable obj defined in loop
            action.triggered.connect(partial(self.add_node, obj))
            self.nodes.append(action)

    def add_node(self, node):
        # TODO: [NOD-4] create the node at mouse point

        if node.is_event_node and NodesRegister.event_nodes:
            self.top_window.show_status_message('Execute node already created')
            return

        # hack: the only way I currently know on how to get an updated pos
        # of the mouse after creating the right click context menu.
        pos = self.top_window._view.mouseCursorPosition()

        command = AddNodeCommand(self.scene, (float(pos.x()), float(pos.y())),
                                 node, 'Add Node')
        self.undo_stack.push(command)


class EditorRunActions(EditorActions):
    def __init__(self, parent):
        super().__init__(parent)

        self.run_act = QAction('Run', self)
        self.run_act.setShortcut(QKeySequence('ctrl+r'))
        self.run_act.triggered.connect(self.run_data)

    def run_data(self):
        NodesRegister.reset_execution_flow()
        self.top_window.show_status_message('Graph executed')

        for node in NodesRegister.get_event_nodes():
            self._find_exec_flow(node.base)
        NodesRegister.reset_nodes_execution()

    def _exec_connected_sockets(self, node):
        for edge in node.node_graphics.data('input_edges'):
            socket = edge.start_socket
            if socket.socket_type == 'execute':
                continue

            edge.transfer_data()

            parent_node = socket.node.base
            if parent_node.was_execute:
                break

            return self._exec_connected_sockets(parent_node)

        return None

    def _find_exec_flow(self, node):
        start_socket = node.get_execute_flow()

        if start_socket.has_edge():
            socket_edge = start_socket.edges[0]
            socket_edge.edge_graphics.update_flow_color('#78DD2A')

            next_node = socket_edge.end_socket.node.base

            self._exec_connected_sockets(next_node)
            return self._find_exec_flow(next_node)

        return None


class NodeMenubar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)

        self._file_actions = EditorFileActions(self)
        self.file_menu = self.addMenu('&File')
        self.add_file_menu()

        self._edit_actions = EditorEditActions(self)
        self.edit_menu = self.addMenu('&Edit')
        self.add_edit_menu()

        self._add_actions = EditorAddActions(self)
        self.add_menu = self.addMenu('&Add')
        self.add_add_menu()

        self._run_actions = EditorRunActions(self)
        self.run_menu = self.addMenu('&Run')
        self.add_run_menu()

    def add_file_menu(self):
        self.file_menu.addAction(self._file_actions.new_file_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self._file_actions.open_file_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self._file_actions.save_file_act)
        self.file_menu.addAction(self._file_actions.save_file_as_act)

    def add_edit_menu(self):
        self.edit_menu.addAction(self._edit_actions.undo_act)
        self.edit_menu.addAction(self._edit_actions.redo_act)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self._edit_actions.duplicate_act)
        self.edit_menu.addAction(self._edit_actions.copy_act)
        self.edit_menu.addAction(self._edit_actions.paste_act)
        self.edit_menu.addAction(self._edit_actions.delete_act)
        self.edit_menu.addSeparator()

    def add_add_menu(self):
        for node in self._add_actions.nodes:
            self.add_menu.addAction(node)

    def add_run_menu(self):
        self.run_menu.addAction(self._run_actions.run_act)
