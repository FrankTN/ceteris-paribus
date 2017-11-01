from PyQt5.QtCore import Qt, QRectF, QLineF
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItem


class Edge(QGraphicsItem):
    def __init__(self, source_node, dest_node):
        super().__init__()
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source_node = source_node
        self.source_point = source_node.get_center()
        self.dest_node = dest_node
        self.dest_point = dest_node.get_center()
        source_node.add_edge(self, True)
        dest_node.add_edge(self, False)

        self.arrow_size = 10

    def get_source(self):
        return self.source_node

    def get_dest(self):
        return self.dest_node

    def set_source(self, new_position):
        self.source_point = new_position
        self.prepareGeometryChange()
        self.update_line()

    def set_dest(self, new_position):
        self.dest_point = new_position
        self.prepareGeometryChange()
        self.update_line()

    def update_line(self):
        self.line.setLine(*self.source_point, *self.dest_point)

    def boundingRect(self):
        return QRectF(*self.source_point, *self.dest_point)

    def paint(self, painter, QStyleOptionGraphicsItem, QWidget_widget=None):
        if not self.source_node or not self.dest_node:
            return

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.line = QLineF(*self.source_point, *self.dest_point)
        painter.drawLine(self.line)

