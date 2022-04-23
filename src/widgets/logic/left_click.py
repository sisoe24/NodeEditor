import logging


from PySide2.QtGui import QPainterPath
from PySide2.QtWidgets import (
    QGraphicsView,
)
from src.widgets.logic.undo_redo import ConnectEdgeCommand, DisconnectEdgeCommand, MoveNodeCommand, SelectCommand
from src.widgets.node_edge import NodeEdgeTmp

from src.widgets.node_graphics import NodeGraphics
from src.widgets.node_socket import SocketGraphics, SocketInput, SocketOutput

LOGGER = logging.getLogger('nodeeditor.left_click')
LOGGER.setLevel(logging.DEBUG)


class LeftClick:
    _mouse_initial_position = True
    _box_selection_mode = False
    _node_drag_mode = False
    _edge_drag_mode = False
    _edge_readjust_mode = False
    _previous_node_selection = None
    _previous_selection = None
    _edge_tmp = None
    _clicked_socket = None
    _edge_tmp = None

    def __init__(self, view, item):
        self.item = item
        self.view = view

    @classmethod
    def assign_mouse(cls, value):
        cls._mouse_initial_position = value

    @classmethod
    def get_mouse(cls):
        return cls._mouse_initial_position

    def _selected_nodes(self):
        """Return the selected nodes inside the scene."""
        return sorted([node for node in self.view._scene.selectedItems()
                       if isinstance(node, NodeGraphics)])

    def _selected_nodes_position(self):
        """Get a the selected nodes position.

        Returns:
            (dict) - the key is the node object and the value is the position.
        """
        return {node: node.pos() for node in self._selected_nodes()}

    def _click_is_node(self):
        return (
            isinstance(self.item, NodeGraphics) and
            not self._node_drag_mode and
            not self._box_selection_mode
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
        def _set_previous_selection(selection):
            if not selection:
                return QPainterPath()

            if isinstance(selection, QPainterPath):
                return selection

            path = QPainterPath()
            path.addPolygon(selection.mapToScene(selection.boundingRect()))
            return path

        command = SelectCommand(
            self.view._scene, previous, current, description)
        self.view.top.undo_stack.push(command)
        self._previous_selection = _set_previous_selection(current)


class LeftClickPress(LeftClick):
    def __init__(self, view, item, event):
        super().__init__(view, item)

        self.view = view
        self.event = event

        # self._mouse_initial_position = event.pos()
        LeftClick._mouse_initial_position = event.pos()

        self.item = item
        if self._click_is_node():
            self._create_selection_command(LeftClick._previous_selection,
                                           self.item, 'Select')

    def _update_node_zValue(self):
        self.item.setZValue(1)
        if hasattr(LeftClick._previous_node_selection, 'setZValue'):
            LeftClick._previous_node_selection.setZValue(0)
        LeftClick._previous_node_selection = self.item

    def on_socket(self, socket):
        LeftClick._clicked_socket = socket
        LeftClick._edge_drag_mode = True
        if isinstance(socket, SocketInput) and socket.has_edge():
            print('redrag edges')

        LeftClick._edge_tmp = NodeEdgeTmp(self.view, socket)
        self.view._scene.addItem(self._edge_tmp.edge_graphics)

    def on_node(self):
        LeftClick._node_drag_mode = True
        LOGGER.debug('Edge drag-mode Enabled')
        LeftClick._nodes_initial_position = self._selected_nodes_position()
        self._update_node_zValue()


class LeftClickRelease(LeftClick):
    def __init__(self, view, item, event):
        super().__init__(view, item)
        print('LeftClick Release')

        self.view = view
        self.event = event
        self.item = item

    def _is_box_selection(self):
        """Check if action is just a box selection."""
        return (
            LeftClick._mouse_initial_position != self.event.pos() and
            not LeftClick._node_drag_mode and
            not LeftClick._edge_drag_mode
        )

    def click_moved(self):
        return LeftClick._mouse_initial_position != self.event.pos()

    def click_is_void(self):
        return not self.item and not self._is_box_selection()

    def _end_node_move(self):
        if LeftClick._node_drag_mode:
            command = MoveNodeCommand(self._selected_nodes_position(),
                                      LeftClick._nodes_initial_position,
                                      'Move Node')
            self.view.top.undo_stack.push(command)
            LeftClick._node_drag_mode = False

    def _end_box_selection(self):
        if self._is_box_selection():
            self._create_selection_command(LeftClick._previous_selection,
                                           self.view._scene.selectionArea(),
                                           'Box Select')
            LeftClick._box_selection_mode = True

    def _delete_tmp_edge(self, msg=None):
        LOGGER.debug('Delete temporary edge')
        if msg:
            LOGGER.debug(msg)
        self.view._scene.removeItem(self._edge_tmp.edge_graphics)

    def _socket_is_invalid(self):
        # if LeftClick._edge_drag_mode:
        return self.item == self._clicked_socket

    def _is_same_socket_type(self, end_socket):
        """Check if input and output socket are the same type."""
        return (isinstance(self._clicked_socket, SocketOutput) and
                isinstance(end_socket, SocketOutput) or
                isinstance(self._clicked_socket, SocketInput) and
                isinstance(end_socket, SocketInput))

    def click_is_on_socket(self, end_socket):
        self._delete_tmp_edge()

        if isinstance(end_socket, SocketInput) and end_socket.has_edge():
            end_socket.remove_edge()

        elif isinstance(end_socket, SocketOutput):
            # invert the sockets if starting point is input to output
            end_socket, LeftClick._clicked_socket = LeftClick._clicked_socket, end_socket

        command = ConnectEdgeCommand(self.view._scene, LeftClick._clicked_socket,
                                     end_socket, 'Connect Edge')
        self.view.top.undo_stack.push(command)

    def release(self):
        if not self.click_moved():
            LeftClick._node_drag_mode = False

        self._end_box_selection()

        if self.click_is_void():
            self._create_selection_command(LeftClick._previous_selection,
                                           None, 'Select')
            return

        self._end_node_move()

        if self._socket_is_invalid():
            self._delete_tmp_edge('End socket is invalid. Delete edge.')
            return

        if LeftClick._edge_drag_mode:
            if isinstance(self.item, SocketGraphics):
                end_socket = self.item
                self.click_is_on_socket(end_socket)

            # elif self._edge_tmp:
            #     if self._edge_readjust_mode:
            #         command = DisconnectEdgeCommand(
            #             self.__start_socket, self.__end_socket,
            #             'Disconnect Edge')
            #         self.top.undo_stack.push(command)
            #         self._edge_readjust_mode = False
            #     self._delete_tmp_edge('Edge release was not on a socket')
