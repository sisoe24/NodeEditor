import logging
from collections import namedtuple

from PySide2.QtCore import Signal, Qt, QEvent
from PySide2.QtGui import QPainter, QMouseEvent
from PySide2.QtWidgets import (
    QGraphicsView
)
from src.widgets.node_edge import NodeEdge, NodeEdgeGraphics, NodeEdgeTmp
from src.widgets.node_graphics import NodeGraphics

from src.widgets.node_socket import Socket, SocketGraphics

LOGGER = logging.getLogger('nodeeditor.view')
LOGGER.setLevel(logging.DEBUG)


class GraphicsView(QGraphicsView):
    mouse_position = Signal(float, float)

    def __init__(self, graphic_scene, parent=None):
        super().__init__(graphic_scene, parent)
        LOGGER.debug('Init Graphics View')

        self._set_flags()

        self.zoom_level = 10
        ZoomRange = namedtuple('ZoomRange', ['min', 'max'])
        self.zoom_range = ZoomRange(5, 15)

        self._debug_zoom()

        self.drag_mode = None
        self._selected_item = None
        self._edge_tmp = None
        self._start_socket = None

    def _debug_zoom(self):
        z = 5.15
        self.scale(z, z)

    @property
    def selected_item(self):
        return self._selected_item

    @selected_item.setter
    def selected_item(self, item):
        # Check if item belongs to a node class
        if hasattr(item, 'parentItem') and isinstance(item.parentItem(), NodeGraphics):
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

    def _leftMouseButtonPress(self, event):
        item = self._get_graphic_item(event)
        LOGGER.debug('Clicked on item: %s', item)

        self.selected_item = item

        if isinstance(item, SocketGraphics):
            self.setDragMode(QGraphicsView.NoDrag)

            self.drag_mode = True
            LOGGER.debug('Drag Mode Enabled')

            self._start_socket = item

            if self._start_socket.has_edge():

                # re assign start socket to the initial starting point
                self._start_socket = self._start_socket.edge.start_point
                item.remove_edge()

            # when drawing the edge, need to set the node z value to stay behind
            # otherwise is not able to recognize the socket if is bellow him.

            self._start_socket.parentItem().setZValue(-1.0)

            self._edge_tmp = NodeEdgeTmp(self, self._start_socket)

        super().mousePressEvent(event)

    def _leftMouseButtonRelease(self, event):
        item = self._get_graphic_item(event)
        LOGGER.debug('Released on item: %s', item)

        # move node above other nodes when selected
        if hasattr(self.selected_item, 'setZValue'):
            # BUG when connecting an output to an input and releasing.
            # the zValue gets reset only for the input and not the output
            # which remains at -1.0, thus connecting back from input to output
            #  does not work
            self.selected_item.setZValue(0)

        if item == self._start_socket:
            LOGGER.debug('End socket is start socket. abort')
            self.scene().removeItem(self._edge_tmp.edge_graphics)
            super().mouseReleaseEvent(event)
            return

        if self.drag_mode:
            if isinstance(item, SocketGraphics):
                end_socket = item

                self.scene().removeItem(self._edge_tmp.edge_graphics)

                # TODO: this should happen also if trying to connect from
                # output to input
                if end_socket.has_edge():
                    end_socket.remove_edge()

                edge = NodeEdge(self, self._start_socket, end_socket)
                end_socket.edge = edge

            elif self._edge_tmp:
                LOGGER.debug('Edge release was not on a socket. delete')
                self.scene().removeItem(self._edge_tmp.edge_graphics)

            self.drag_mode = False
            LOGGER.debug('Drag Mode Disabled')

        self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def _rightMouseButtonPress(self, event):
        """Debug use."""
        item = self._get_graphic_item(event)
        if isinstance(item, SocketGraphics):
            LOGGER.info(item)
        elif isinstance(item, NodeEdgeGraphics):
            LOGGER.info(item)
        elif hasattr(item, 'parentItem') and isinstance(item.parentItem(), NodeGraphics):
            item = item.parentItem()
            LOGGER.info('Node %s, edges: %s, zValue: %s', item,
                        len(item._edges), item.zValue())

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
        if self.drag_mode:
            self.scene().update()

        self._update_mouse_position(event)
        return super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()

        selected_items = self.scene().selectedItems()

        if key == Qt.Key_Delete and selected_items:

            for item in selected_items:

                if isinstance(item, NodeEdgeGraphics):
                    item.delete_edge()
                elif isinstance(item, NodeGraphics):
                    item.delete_node()

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
