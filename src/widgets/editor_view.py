import logging
from collections import namedtuple

from PySide2.QtCore import Signal, Qt, QEvent
from PySide2.QtGui import QPainter, QMouseEvent
from PySide2.QtWidgets import (
    QGraphicsView
)

from src.widgets.node_socket import SocketGraphics

LOGGER = logging.getLogger('nodeeditor.view')
LOGGER.setLevel(logging.DEBUG)


class GraphicsView(QGraphicsView):
    mouse_position = Signal(str)

    def __init__(self, graphic_scene, parent=None):
        super().__init__(graphic_scene, parent)
        LOGGER.info('Init Graphics View')

        self._set_flags()

        self.zoom_level = 10
        ZoomRange = namedtuple('ZoomRange', ['min', 'max'])
        self.zoom_range = ZoomRange(5, 15)

        # self._debug_zoom()

    def _debug_zoom(self):
        z = 3.65
        self.scale(z, z)

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

    def _get_graphic_item(self, event):
        """Get the item under the cursor.

        Returns:
            any: the object item under the cursor
        """
        return self.itemAt(event.pos())

    def mouseMoveEvent(self, event):
        self._update_mouse_position(event)
        return super().mouseMoveEvent(event)

    def _update_mouse_position(self, event):
        """Emit a signal to update mouse position label status."""
        pos = self.mapToScene(event.pos())
        self.mouse_position.emit(f'{round(pos.x())}, {round(pos.y())}')

    def mousePressEvent(self, event):
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

    def mouseReleaseEvent(self, event):
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

    @staticmethod
    def _drag_mouse_event(event):
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

    def _middleMouseButtonPress(self, event):
        """Release event for the middle button.

        This function will mimic a Left Mouse Button Press event and set the
        DragMode to ScrollHandDrag.

        Args:
            event (QEvent): the mouse event.
        """
        # the release event is for the select box
        release_event = QMouseEvent(
            QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
            Qt.LeftButton, Qt.NoButton, event.modifiers()
        )
        super().mousePressEvent(release_event)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(self._drag_mouse_event(event))

    def _middleMouseButtonRelease(self, event):
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
        if isinstance(item, SocketGraphics):
            event.ignore()
        else:
            super().mousePressEvent(event)

    def _leftMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def _rightMouseButtonPress(self, event):
        LOGGER.info(self._get_graphic_item(event))
        super().mousePressEvent(event)

    def _rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Override wheel event to create the zoom effect

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
