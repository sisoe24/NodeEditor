
from PySide2.QtCore import Qt, QRectF, QPointF

from PySide2.QtGui import (
    QPainter,
    QPolygonF,
    QPen,
    QPainterPath

)
from PySide2.QtWidgets import (
    QGraphicsItem
)


class NodeEdgeCutline(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._pen = QPen(Qt.white)
        self._pen.setWidth(2.0)
        self._pen.setDashPattern([3, 3])

        self.line_points = []
        self.setZValue(2)

    def boundingRect(self):
        return self.shape().boundingRect()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)

    def shape(self):
        poly = QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path
