from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsLineItem


class Edge(QGraphicsLineItem):
    def __init__(self, source_node, dest_node):
        super().__init__(source_node.get_center().x(), source_node.get_center().y(), dest_node.get_center().x(),
                         dest_node.get_center().y())
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source_node = source_node
        self.dest_node = dest_node
        source_node.add_edge(self, True)
        dest_node.add_edge(self, False)
        self.arrow_size = 10

    def get_source(self):
        return self.source_node

    def get_dest(self):
        return self.dest_node

    def set_source(self, new_position: QPointF):
        self.setLine(new_position.x(), new_position.y(), self.dest_node.get_center().x(),
                     self.dest_node.get_center().y())
        self.update()

    def set_dest(self, new_position: QPointF):
        self.setLine(self.source_node.get_center().x(), self.source_node.get_center().y(),
                     new_position.x(), new_position.y())

        self.dest_point = new_position
        self.update()
