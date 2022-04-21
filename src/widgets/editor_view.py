import logging
from collections import namedtuple

from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QPainter, QMouseEvent, QPainterPath
from PySide2.QtWidgets import (
    QGraphicsView,
)

from src.widgets.node_graphics import NodeGraphics
from src.widgets.node_edge import NodeEdge, NodeEdgeGraphics, NodeEdgeTmp
from src.widgets.node_socket import SocketGraphics, SocketInput, SocketOutput

from src.widgets.logic.undo_redo import (
    DisconnectEdgeCommand,
    MoveNodeCommand,
    ConnectEdgeCommand,
    DeleteNodeCommand,
    SelectCommand,
)

LOGGER = logging.getLogger('nodeeditor.view')
LOGGER.setLevel(logging.DEBUG)


class GraphicsView(QGraphicsView):
    mouse_position = Signal(float, float)

    def __init__(self, graphic_scene, parent=None):
        super().__init__(graphic_scene, parent)
        LOGGER.debug('Init Graphics View')

        self.top = self.topLevelWidget()

        self._set_flags()

        self.zoom_level = 10
        ZoomRange = namedtuple('ZoomRange', ['min', 'max'])
        self.zoom_range = ZoomRange(5, 15)

        self._debug_zoom()

        self._edge_drag_mode = None
        self._edge_readjust = None
        self._node_drag_mode = None
        self._selected_item = None
        self._edge_tmp = None
        self._clicked_socket = None

        self._previous_single_selection = None
        self._previous_box_selection = None
        self._previous_selection = None
        self._node_initial_position = None

        self._box_selection = False

        self._mouse_initial_position = None
        self._scene = self.scene()
        self._scene.selectionChanged.connect(self._update_selection)

    def _debug_zoom(self):
        z = 1.15
        self.scale(z, z)

    @property
    def selected_item(self):
        return self._selected_item

    @selected_item.setter
    def selected_item(self, item):
        # Check if item belongs to a node class
        if (
            hasattr(item, 'parentItem') and
            isinstance(item.parentItem(), NodeGraphics)
        ):
            self._selected_item = item.parentItem()
            self._selected_item.setZValue(1)
        else:
            self._selected_item = item

    def _set_flags(self):
        """Set up some flags for the UI view."""
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)

        # Disable scrollbar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # When any visible part of the scene changes or is re-exposed,
        # QGraphicsView will update the entire viewport.
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # The point under the mouse is used as the anchor or the user resizes
        # the view or when the view is transformed.
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # default action for the view when pressing and dragging the mouse over
        # the viewport.
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def _get_graphic_item(self, event: QMouseEvent):
        """Get the item under the cursor.

        Returns:
            any: the object item under the cursor
        """
        return self.itemAt(event.pos())

    def _update_mouse_position(self, event: QMouseEvent):
        """Emit a signal to update mouse position label status."""
        pos = self.mapToScene(event.pos())
        self.mouse_position.emit(pos.x(), pos.y())

    @staticmethod
    def _drag_mouse_event(event: QMouseEvent):
        """Create the drag mouse event.

        This function mimic a Left Mouse button drag while the middle mouse btn
        is clicked.

        Args:
            event (QEvent): the mouse event.

        Returns:
            QMouseEvent: The fake drag mouse event.
        """
        return QMouseEvent(
            event.type(), event.localPos(), event.screenPos(),
            Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers()
        )

    def _middleMouseButtonPress(self, event: QMouseEvent):
        """Release event for the middle button.

        This function will mimic a Left Mouse Button Press event and set the
        DragMode to ScrollHandDrag.

        Args:
            event (QEvent): the mouse event.
        """
        # the release event is for the select box
        # release_event = QMouseEvent(
        #     QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
        #     Qt.LeftButton, Qt.NoButton, event.modifiers()
        # )
        # super().mousePressEvent(release_event)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(self._drag_mouse_event(event))

    def _middleMouseButtonRelease(self, event: QMouseEvent):
        """Release event for the middle button.

        This function will mimic a Left Mouse Button Release event and set the
        DragMode to NoDrag.

        Args:
            event (QEvent): the mouse event.
        """
        super().mouseReleaseEvent(self._drag_mouse_event(event))
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def _item_is_node(self):
        return (
            isinstance(self.selected_item, NodeGraphics) and
            not self._node_drag_mode and
            not self._box_selection
        )

    def _leftMouseButtonPress(self, event):
        item = self._get_graphic_item(event)
        LOGGER.debug('Clicked on item: %s', item)
        self._mouse_initial_position = event.pos()

        self.selected_item = item
        if self._item_is_node():
            self._create_selection_command(self._previous_selection,
                                           self.selected_item, 'Select')

        if isinstance(item, SocketGraphics):
            self.setDragMode(QGraphicsView.NoDrag)

            self._edge_drag_mode = True
            LOGGER.debug('Drag Mode Enabled')

            self._clicked_socket = item

            # input socket should only have 1 edge connected
            if isinstance(item, SocketInput) and item.has_edge():
                LOGGER.debug('SocketInput has an edge connected already')

                self._edge_readjust = True

                # FIXME: ugly
                self.__start_socket = item.edge.start_socket
                self.__end_socket = item.edge.end_socket

                # REVIEW: might not need this after re assign always start to output
                # re assign start socket to the initial starting point
                self._clicked_socket = (
                    self.__end_socket if isinstance(self.__start_socket, SocketInput)
                    else self.__start_socket
                )

                # delete the original edge
                item.remove_edge()

            # FIXME: when drawing the edge, need to set the node zValue to stay
            # behind the socket otherwise will not able to recognize it
            self._clicked_socket.parentItem().setZValue(-1.0)

            self._edge_tmp = NodeEdgeTmp(self, self._clicked_socket)

        elif isinstance(self.selected_item, NodeGraphics):
            print('moving nodes')
            self._node_drag_mode = True
            self._nodes_initial_position = self._selected_nodes_position()

        super().mousePressEvent(event)

    def _delete_tmp_edge(self, msg=None):
        LOGGER.debug('Delete temporary edge')
        if msg:
            LOGGER.debug(msg)
        self.scene().removeItem(self._edge_tmp.edge_graphics)

    def _is_same_socket_type(self, end_socket):
        """Check if input and output socket are the same type."""
        return (isinstance(self._clicked_socket, SocketOutput) and
                isinstance(end_socket, SocketOutput) or
                isinstance(self._clicked_socket, SocketInput) and
                isinstance(end_socket, SocketInput))

    def _is_box_selection(self, event):
        """Check if action is just a box selection."""
        return (
            self._mouse_initial_position != event.pos() and
            not self._node_drag_mode and
            not self._edge_drag_mode
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

        command = SelectCommand(self._scene, previous, current, description)
        self.top.undo_stack.push(command)
        self._previous_selection = _set_previous_selection(current)

    def _update_selection(self):
        """When scene selection changes do something.

        Currently, when selection is less than 1, it does set the flag
        `_box_selection` to `False`.
        """
        nodes = self._selected_nodes()
        if len(nodes) <= 1:
            self._box_selection = False

    def _selected_nodes(self):
        """Return the selected nodes inside the scene."""
        return [node for node in self.scene().selectedItems()
                if isinstance(node, NodeGraphics)]

    def _selected_nodes_position(self):
        """Get a the selected nodes position.

        Returns:
            (dict) - the key is the node object and the value is the position.
        """
        return {node: node.pos() for node in self._selected_nodes()}

    def _leftMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

        if self._mouse_initial_position == event.pos():
            self._node_drag_mode = False

        item = self._get_graphic_item(event)
        LOGGER.debug('Released on item: %s', item)

        if self._is_box_selection(event):
            self._create_selection_command(self._previous_selection,
                                           self.scene().selectionArea(),
                                           'Box Select')
            self._box_selection = True

        if not item and not self._is_box_selection(event):
            self._create_selection_command(
                self._previous_selection, None, 'Select')
            return

        if self._node_drag_mode:
            # TODO?: trigger only if node was moved
            command = MoveNodeCommand(self._selected_nodes_position(),
                                      self._nodes_initial_position,
                                      'Move Node')
            self.top.undo_stack.push(command)
            self._node_drag_mode = False

        # move node above other nodes when selected
        if hasattr(self.selected_item, 'setZValue'):
            # BUG: there might a bug when connected from input to output
            # where the zValue does not get reset properly
            self.selected_item.setZValue(0)

        if self._edge_drag_mode:

            if item == self._clicked_socket:
                self._delete_tmp_edge('End socket is start socket. abort')
                return

            if isinstance(item, SocketGraphics):
                end_socket = item

                if self._is_same_socket_type(end_socket):
                    self._delete_tmp_edge(
                        'Start and End socket are both same type sockets.')
                    return

                self._delete_tmp_edge()

                if isinstance(end_socket, SocketInput) and end_socket.has_edge():
                    end_socket.remove_edge()
                elif isinstance(end_socket, SocketOutput):
                    # invert the sockets if starting point is input to output
                    end_socket, self._clicked_socket = self._clicked_socket, end_socket

                command = ConnectEdgeCommand(self._clicked_socket, end_socket,
                                             'Connect Edge')
                self.top.undo_stack.push(command)

            # Review: simplify the condition
            elif self._edge_tmp:
                if self._edge_readjust:
                    command = DisconnectEdgeCommand(
                        self.__start_socket, self.__end_socket,
                        'Disconnect Edge')
                    self.top.undo_stack.push(command)
                    self._edge_readjust = False
                self._delete_tmp_edge('Edge release was not on a socket')

            self._edge_drag_mode = False
            LOGGER.debug('Drag Mode Disabled')

        self.setDragMode(QGraphicsView.RubberBandDrag)

    def _rightMouseButtonPress(self, event):
        """Debug use."""
        item = self._get_graphic_item(event)

        if isinstance(item, (SocketGraphics, NodeEdgeGraphics)):
            print(item.repr())
        elif (
            hasattr(item, 'parentItem') and
            isinstance(item.parentItem(), NodeGraphics)
        ):
            print(item.parentItem().repr())

        super().mousePressEvent(event)

    def _rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Override the mousePressEvent event."""
        button = event.button()

        if button == Qt.MidButton:
            self._middleMouseButtonPress(event)
        elif button == Qt.LeftButton:
            self._leftMouseButtonPress(event)
        elif button == Qt.RightButton:
            self._rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Override the mouseReleaseEvent event."""
        button = event.button()

        if button == Qt.MidButton:
            self._middleMouseButtonRelease(event)
        elif button == Qt.LeftButton:
            self._leftMouseButtonRelease(event)
        elif button == Qt.RightButton:
            self._rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._edge_drag_mode:
            self.scene().update()

        self._update_mouse_position(event)
        return super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()

        selected_items = self.scene().selectedItems()

        if key == Qt.Key_Delete and selected_items:

            def obj_list(obj):
                return [_ for _ in selected_items if isinstance(_, obj)]

            # --- FIXME: I have to delete the edges before deleting the nodes or
            # --- it might cause some problems when delete an edge after deleting
            # --- its parent node (which deletes the edge)
            # XXX: I might not need anymore because the edge is not selectable
            # for edge in obj_list(NodeEdgeGraphics):
            #     command = DeleteEdgeCommand(edge, self.scene(), 'Delete edge')
            #     self.top.undo_stack.push(command)

            self.top.undo_stack.beginMacro('Delete Node')
            for node in obj_list(NodeGraphics):
                command = DeleteNodeCommand(node, self.scene(), 'Delete node')
                self.top.undo_stack.push(command)
            self.top.undo_stack.endMacro()

        return super().keyPressEvent(event)

    def wheelEvent(self, event):
        """Override wheel event to create the zoom effect.

        The zoom is based on a zoom_factor and zoom_level. If zoom is
        bigger/lower than the zoom_level, will be clamped and stop from zooming
        in/out.

        Args:
            event (QEvent): the mouse event.
        """
        zoom_factor = 1.25
        zoom_step = 1

        # Check if rolling is forward: zoomin in
        if event.angleDelta().y() > 0:
            zoom = zoom_factor
            self.zoom_level += zoom_step
        else:
            zoom = 1 / zoom_factor
            self.zoom_level -= zoom_step

        clamped = False

        # If zoom level goes beyond zoom range, then "clamp" it and reset it
        if self.zoom_level < self.zoom_range.min:
            self.zoom_level, clamped = self.zoom_range.min, True

        if self.zoom_level > self.zoom_range.max:
            self.zoom_level, clamped = self.zoom_range.max, True

        if not clamped:
            self.scale(zoom, zoom)
