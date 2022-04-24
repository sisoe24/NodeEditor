import logging
from collections import namedtuple

from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QPainter, QMouseEvent, QPainterPath
from PySide2.QtWidgets import (
    QApplication,
    QGraphicsView,
)
from src.widgets.logic.left_click import LeftClick, LeftClickPress, LeftClickRelease
from src.widgets.node_edge_cutline import NodeEdgeCutline

from src.widgets.node_graphics import NodeGraphics
from src.widgets.node_edge import NodeEdge, NodeEdgeGraphics, NodeEdgeTmp
from src.widgets.node_socket import SocketGraphics, SocketInput, SocketOutput

from src.widgets.logic.undo_redo import (
    DeleteEdgeCommand,
    DeleteNodeCommand,
)

LOGGER = logging.getLogger('nodeeditor.view')
LOGGER.setLevel(logging.DEBUG)


class GraphicsView(QGraphicsView):
    mouse_position = Signal(float, float)
    graph_debug = Signal(str)

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
        self._edge_cut_mode = None
        self._edge_readjust_mode = None
        self._node_drag_mode = None
        self._box_selection_mode = None

        self._selected_item = None
        self._edge_tmp = None
        self._clicked_socket = None

        self._previous_selection = None
        self._previous_node_selection = None

        self._mouse_pos_view = None
        self._mouse_pos_scene = None
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

    def _get_graphic_item(self, pos):
        """Get the item under the cursor.

        Returns:
            any: the object item under the cursor
        """
        return self.itemAt(pos)

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

    def _update_selection(self):
        """When scene selection changes do something.

        Currently, when selection is less than 1, it does set the flag
        `_box_selection_mode` to `False`.
        """
        nodes = self.selected_nodes()
        if len(nodes) <= 1:
            LeftClick._box_selection_mode = False

    def selected_nodes(self):
        """Return the selected nodes inside the scene."""
        return sorted([node for node in self.scene().selectedItems()
                       if isinstance(node, NodeGraphics)])

    def _leftMouseButtonPress(self, event):
        # super().mousePressEvent(event)
        item = self._get_graphic_item(event.pos())
        LOGGER.debug('Clicked on item: %s', item)

        self.selected_item = item

        self.left_click = LeftClickPress(self, self.selected_item, event)

        if isinstance(item, SocketGraphics):
            self.setDragMode(QGraphicsView.NoDrag)

            # REVIEW: dont like this here
            self._edge_drag_mode = True

            self.left_click.on_socket(item)

        elif isinstance(self.selected_item, NodeGraphics):
            super().mousePressEvent(event)
            self.left_click.on_node()
            return

        super().mousePressEvent(event)

    def _leftMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

        item = self._get_graphic_item(event.pos())

        click = LeftClickRelease(self, item, event)
        click.release()

        self.setDragMode(QGraphicsView.RubberBandDrag)

    def _rightMouseButtonPress(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self._edge_cut_mode = True
            QApplication.setOverrideCursor(Qt.CrossCursor)
            self._cut_edge = NodeEdgeCutline()
            self._scene.addItem(self._cut_edge)
            return

        super().mousePressEvent(event)

    def _rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

        if self._edge_cut_mode:

            for n in self._cut_edge.line_points:
                pos = self.mapFromScene(n.toPoint())
                item = self._get_graphic_item(pos)
                if isinstance(item, NodeEdgeGraphics):
                    command = DeleteEdgeCommand(
                        item, self._scene, 'Delete edge')
                    self.top.undo_stack.push(command)

            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self._cut_edge.line_points = []
            self._edge_cut_mode = False
            self._cut_edge.update()
            self._scene.removeItem(self._cut_edge)
            return

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
        self._mouse_pos_view = event.pos()

        self._mouse_pos_scene = self.mapToScene(event.pos())
        self.mouse_position.emit(self._mouse_pos_scene.x(),
                                 self._mouse_pos_scene.y())

        if self._edge_drag_mode:
            self.left_click.update_view()
            # self._edge_tmp.edge_graphics.update()

        if self._edge_cut_mode:
            pos = self.mapToScene(event.pos())
            self._cut_edge.line_points.append(pos)
            self._cut_edge.update()

        return super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_I:
            item = self._get_graphic_item(self._mouse_pos_view)

            if not item:
                return

            if isinstance(item, (SocketGraphics, NodeEdgeGraphics)):
                self.graph_debug.emit(item.repr())
            elif (
                hasattr(item, 'parentItem') and
                isinstance(item.parentItem(), NodeGraphics)
            ):
                self.graph_debug.emit(item.parentItem().repr())

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
