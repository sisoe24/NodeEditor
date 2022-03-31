import logging
from math import floor, ceil

from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QColor, QBrush, QPen
from PySide2.QtWidgets import (
    QGraphicsScene,
    QGraphicsItem
)


LOGGER = logging.getLogger('nodeeditor.scene')


class GraphicScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        LOGGER.info('Init Graphical Scene')

        self._grid_pen = QPen(QColor("#282828"))
        self._grid_pen.setWidth(2)

        self.setBackgroundBrush(QColor("#393939"))

        # self._debug_content()

    def _debug_content(self):
        """Generate debug content.

        Create a simple movable rectangle with border and fill color.
        """
        fill = QBrush(Qt.black)
        border = QPen(Qt.red)
        border.setWidth(5)

        rect = self.addRect(0, 0, 100, 100, border, fill)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Get scene bounding size converted as integers for the range loop
        left = round(rect.left())
        right = round(rect.right())
        top = round(rect.top())
        bottom = round(rect.bottom())

        x_points = []
        y_points = []

        # TODO: change grid_size based on zoom level
        grid_size = 20

        # Draw the grid
        for x in range(left, right, grid_size):
            x_points.append(QPoint(x, top))

            for y in range(top, bottom, grid_size):
                y_points.append(QPoint(x, y))

        painter.setPen(self._grid_pen)
        painter.drawPoints(x_points + y_points)


class Scene:
    def __init__(self):
        LOGGER.info('Init Scene')

        self.scene_width = 64000
        self.scene_height = 64000

        self.graphics_scene = GraphicScene()
        self.graphics_scene.setSceneRect(-self.scene_width // 2,
                                         -self.scene_height // 2,
                                         self.scene_width, self.scene_height)
