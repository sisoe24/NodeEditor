
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
        self._pen.setWidth(1.0)
        self._pen.setDashPattern([3, 3])

        self.line_points = []

    def boundingRect(self):
        return QRectF(0, 0, 1, 1)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
