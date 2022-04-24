import contextlib
import logging


from PySide2.QtGui import QPainterPath
from PySide2.QtWidgets import (
    QGraphicsView,
)
from src.widgets.logic.undo_redo import BoxSelectCommand, ConnectEdgeCommand, DisconnectEdgeCommand, MoveNodeCommand, SelectCommand
from src.widgets.node_edge import NodeEdgeTmp

from src.widgets.node_graphics import NodeGraphics
from src.widgets.node_socket import SocketGraphics, SocketInput, SocketOutput

LOGGER = logging.getLogger('nodeeditor.left_click')
LOGGER.setLevel(logging.DEBUG)


class LeftClick:

    mode_selection_box = False
    mode_drag_node = False
    mode_drag_edge = False
    mode_drag_tmp_edge = False

    nodes_initial_position = None
    mouse_initial_position = None

    selection_node_previous = None
    selection_group_previous = None

    selection_previous_node = None
    selection_previous_box = None

    edge_tmp = None

    socket_clicked = None
    socket_start = None
    socket_end = None

    def __init__(self, view, item):
        self.item = item
        self.view = view

    def _selected_nodes_position(self):
        """Get a the selected nodes position.

        Returns:
            (dict) - the key is the node object and the value is the position.
        """
        return {node: node.pos() for node in self.view._selected_nodes()}

    def _click_is_node(self):
        return (
            isinstance(self.item, NodeGraphics) and
            not self.mode_drag_node and
            not self.mode_selection_box
        )

    def _create_selection_command(self, previous, current, description):
        """Update the selection undo redo command.

        Create the undo redo command stack for the selection. Selection can be
        a single node select or a box select.

        Args:
            previous (any): the previous selection
            current (any): the current selection
            description (str): the undo redo description
        """
        command = SelectCommand(
            self.view._scene, previous, current, description)
        self.view.top.undo_stack.push(command)
        LeftClick.selection_previous_node = current


class LeftClickPress(LeftClick):
    def __init__(self, view, item, event):
        super().__init__(view, item)

        self.view = view
        self.event = event

        LeftClick.mouse_initial_position = event.pos()

        self.item = item
        if self._click_is_node():
            self._create_selection_command(LeftClick.selection_previous_node,
                                           self.item, 'Select')

    @staticmethod
    def _re_connect_edge(socket):
        LOGGER.debug('SocketInput has an edge connected already')
        LeftClick.mode_drag_tmp_edge = True

        LeftClick.socket_start = socket.edge.start_socket
        LeftClick.socket_end = socket.edge.end_socket

        # Invert the sockets if click starts at a output socket
        LeftClick.socket_clicked = (
            LeftClick.socket_end if isinstance(LeftClick.socket_start, SocketInput)
            else LeftClick.socket_start
        )

        socket.remove_edge()

    def on_socket(self, socket):
        LeftClick.socket_clicked = socket
        LeftClick.mode_drag_edge = True

        if isinstance(socket, SocketInput) and socket.has_edge():
            self._re_connect_edge(socket)

        LeftClick.edge_tmp = NodeEdgeTmp(self.view, LeftClick.socket_clicked)
        self.view.scene().addItem(LeftClick.edge_tmp.edge_graphics)

    def _update_node_zValue(self):
        self.item.setZValue(1)
        if hasattr(LeftClick.selection_node_previous, 'setZValue'):
            LeftClick.selection_node_previous.setZValue(0)
        LeftClick.selection_node_previous = self.item

    def on_node(self):
        LOGGER.debug('Edge drag-mode Enabled')

        LeftClick.mode_drag_node = True
        LeftClick.nodes_initial_position = self._selected_nodes_position()

        self._update_node_zValue()

    def update_view(self):
        with contextlib.suppress(AttributeError):
            LeftClick.edge_tmp.edge_graphics.update()


class LeftClickRelease(LeftClick):
    def __init__(self, view, item, event):
        super().__init__(view, item)
        self.view = view
        self.event = event
        self.item = item

        self.mode_selection_box = False

    def _click_moved(self):
        return LeftClick.mouse_initial_position != self.event.pos()

    def _click_is_void(self):
        return not self.item and not self._is_box_selection()

    def _end_node_move(self):
        if LeftClick.mode_drag_node:
            command = MoveNodeCommand(self._selected_nodes_position(),
                                      LeftClick.nodes_initial_position,
                                      'Move Node')
            self.view.top.undo_stack.push(command)
            LeftClick.mode_drag_node = False

    def _is_box_selection(self):
        """Return `True` if action is a box selection."""
        return (
            LeftClick.mouse_initial_position != self.event.pos() and
            not LeftClick.mode_drag_node and
            not LeftClick.mode_drag_edge
        )

    def _create_box_select_command(self):
        scene = self.view.scene()
        command = BoxSelectCommand(scene, LeftClick.selection_previous_box,
                                   scene.selectionArea(), 'Box Select')
        self.view.top.undo_stack.push(command)
        LeftClick.selection_previous_box = scene.selectionArea()
        LeftClick.mode_selection_box = True

    def _end_box_selection(self):
        if self._is_box_selection():
            self._create_box_select_command()

    def _delete_tmp_edge(self, msg=None):
        LOGGER.debug('Delete temporary edge. ' + (msg or ''))
        self.view._scene.removeItem(LeftClick.edge_tmp.edge_graphics)
        LeftClick.edge_tmp = None

    def _socket_is_invalid(self):
        return self.item == LeftClick.socket_clicked

    @staticmethod
    def _is_same_socket_type(end_socket):
        """Check if input and output socket are the same type."""
        return (isinstance(LeftClick.socket_clicked, SocketOutput) and
                isinstance(end_socket, SocketOutput) or
                isinstance(LeftClick.socket_clicked, SocketInput) and
                isinstance(end_socket, SocketInput))

    def click_is_on_socket(self, end_socket):
        self._delete_tmp_edge()

        if isinstance(end_socket, SocketInput) and end_socket.has_edge():
            end_socket.remove_edge()

        elif isinstance(end_socket, SocketOutput):
            # invert the sockets if starting point is input to output
            end_socket, LeftClick.socket_clicked = LeftClick.socket_clicked, end_socket

        command = ConnectEdgeCommand(self.view._scene,
                                     LeftClick.socket_clicked,
                                     end_socket, 'Connect Edge')
        self.view.top.undo_stack.push(command)

    def _readjust_edge(self):
        if LeftClick.mode_drag_tmp_edge:
            command = DisconnectEdgeCommand(LeftClick.socket_start,
                                            LeftClick.socket_end,
                                            'Disconnect Edge')
            self.view.top.undo_stack.push(command)
            LeftClick.mode_drag_tmp_edge = False

    def release(self):
        if not self._click_moved():
            LeftClick.mode_drag_node = False

        self._end_box_selection()

        if self._click_is_void():
            self._create_selection_command(LeftClick.selection_previous_node,
                                           None, 'Select')
            return

        self._end_node_move()

        if LeftClick.mode_drag_edge:

            if self._socket_is_invalid():
                self._delete_tmp_edge('End socket is invalid. Delete edge.')
                return

            if isinstance(self.item, SocketGraphics):
                self.click_is_on_socket(self.item)

            elif LeftClick.edge_tmp:
                self._readjust_edge()
                self._delete_tmp_edge('Edge release was not on a socket')
