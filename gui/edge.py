from PyQt5.QtCore import QLineF, Qt, QRectF
from PyQt5.QtGui import QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsItem


class Edge(QGraphicsItem):
    def __init__(self, source_node, dest_node):
        super().__init__()
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source_node = source_node
        self.dest_node = dest_node
        source_node.add_edge(self)
        dest_node.add_edge(self)

        self.arrow_size = 10
        self.adjust()

    def get_source(self):
        return self.source_node

    def get_dest(self):
        return self.dest_node

    def boundingRect(self):
        return QRectF(self.source_point, self.dest_point)

    def adjust(self):
        if not self.source_node or not self.dest_node:
            return

        line = QLineF(self.mapFromItem(self.source_node, 50, 50), self.mapFromItem(self.dest_node, 50, 50))
        self.source_point = line.p1()
        self.dest_point = line.p2()

        self.prepareGeometryChange()

    def paint(self, painter, QStyleOptionGraphicsItem, QWidget_widget=None):
        if not self.source_node or not self.dest_node:
            return

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.line = QLineF(self.source_point, self.dest_point)
        painter.drawLine(self.line)

