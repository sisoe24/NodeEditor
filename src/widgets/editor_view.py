import logging
from collections import namedtuple

from PySide2.QtCore import Signal, Qt, QEvent
from PySide2.QtGui import QPainter, QMouseEvent
from PySide2.QtWidgets import (
    QGraphicsView
)

LOGGER = logging.getLogger('nodeeditor.view')


class GraphicsView(QGraphicsView):
    mouse_position = Signal(str)

    def __init__(self, graphic_scene, parent=None):
        super().__init__(graphic_scene, parent)
        LOGGER.info('Init Graphics View')

        self._set_flags()

        self.zoom_level = 10
        ZoomRange = namedtuple('ZoomRange', ['min', 'max'])
        self.zoom_range = ZoomRange(5, 15)

        self._debug_zoom()

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

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.mouse_position.emit(f'{x}, {y}')
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Override the mousePressEvent event."""
        button = event.button()

        if button == Qt.MidButton:
            self.middleMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Override the mouseReleaseEvent event."""
        button = event.button()

        if button == Qt.MidButton:
            self.middleMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    @ staticmethod
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

    def middleMouseButtonPress(self, event):
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

    def middleMouseButtonRelease(self, event):
        """Release event for the middle button.

        This function will mimic a Left Mouse Button Release event and set the
        DragMode to NoDrag.

        Args:
            event (QEvent): the mouse event.
        """
        super().mouseReleaseEvent(self._drag_mouse_event(event))
        self.setDragMode(QGraphicsView.RubberBandDrag)

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
