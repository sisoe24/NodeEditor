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
from src.utils.graph_state import load_file, save_file

from src.widgets.logic.undo_redo import AddNodeCommand
from src.widgets.node_graphics import NodesRegister


class EditorFileActions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.top_window = self.topLevelWidget()
        self.undo_stack = self.top_window.undo_stack
        self.scene = self.top_window._scene

        self.editor_file = None

        self.new_file_act = QAction('New File', self)
        self.new_file_act.triggered.connect(self.new_file)

        self.open_file_act = QAction('Open File...', self)
        self.open_file_act.triggered.connect(self.open_file)

        self.save_file_act = QAction('Save File', self)
        self.save_file_act.triggered.connect(self.save_file)

        self.save_file_as_act = QAction('Save File As...', self)
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

        self.scene.clear()
        self.undo_stack.clear()

    def open_file(self):
        if self._cancel_action():
            return

        # TODO: make scripts path absolute
        file, _ = QFileDialog.getOpenFileName(caption='Open File...',
                                              dir='scripts',
                                              filter='*.json')
        if file:
            load_file(self.scene, file)
            self.editor_file = file
            self.top_window.setWindowTitle(os.path.basename(file))
            self.top_window.show_status_message('File Loaded')
            self.undo_stack.clear()


class EditorEditActions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.top_window = self.topLevelWidget()
        self.undo_stack = self.top_window.undo_stack
        self.scene = self.top_window._scene

        self.undo_act = self.undo_stack.createUndoAction(self, 'Undo')
        self.undo_act.setShortcut(QKeySequence.Undo)

        self.redo_act = self.undo_stack.createRedoAction(self, 'Redo')
        self.redo_act.setShortcut(QKeySequence.Redo)


class EditorAddActions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.top_window = self.topLevelWidget()
        self.undo_stack = self.top_window.undo_stack
        self.scene = self.top_window._scene

        self.nodes = []

        nodes = NodesRegister.get_avaliable_nodes().items()
        for node, obj in nodes:
            action = QAction(node, self)

            # XXX: lambda does not work in this case, don't know why
            # err: Cell variable obj defined in loop
            action.triggered.connect(partial(self.add_node, obj))
            self.nodes.append(action)

    def add_node(self, node):
        # TODO: create the node at mouse point
        x, y = self.top_window.mouse_position.text().split(',')
        command = AddNodeCommand(self.scene, (float(x), float(y)),
                                 node, 'Add Node')
        self.undo_stack.push(command)


class NodeMenubar(QMenuBar):
    def __init__(self, parent=None):
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

    def add_add_menu(self):
        for node in self._add_actions.nodes:
            self.add_menu.addAction(node)
