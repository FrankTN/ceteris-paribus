from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsPathItem

from gui.dialogs import OrganSettingsDialog, InputSettingsDialog


class GraphNode(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(0, 0, 100, 100)
        self.setPos(x,y)
        self.edge_list = []
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)
        self.name = ""

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            pass
        return QGraphicsRectItem.itemChange(self, change, value)

    def add_edge(self, edge):
        self.edge_list.append(edge)
        edge.adjust()

    def edges(self):
        return self.edge_list

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        rect = self.boundingRect()
        if self.isSelected():
            QPainter.drawRect(rect)

        QPainter.fillRect(rect, QBrush(Qt.lightGray))
        QPainter.drawText(rect, self.name)

        for edge in self.edge_list:
            edge.paint(QPainter, QStyleOptionGraphicsItem)
            edge.adjust()



class InNode(GraphNode):
    def __init__(self, x, y, model):
        super().__init__(x, y)
        self.name = "Input"
        self.model = model

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent, **kwargs):
        dialog = InputSettingsDialog(self.model)
        dialog.exec_()
        print("clicked: Input")

class OrganNode(GraphNode):
    def __init__(self, organ):
        super().__init__(*organ.pos)
        self.organ = organ
        self.name = organ.get_name()

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent, **kwargs):
        dialog = OrganSettingsDialog(self.organ)
        dialog.exec_()
        print("clicked: " + self.organ.get_name())


