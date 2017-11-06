""" Module containing the definitions of different node types. Currently, the Input and Output nodes are special, the
    other nodes should all contain Organ data."""
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsPathItem

from gui.dialogs import OrganSettingsDialog, InputSettingsDialog, OutputSettingsDialog
from gui.edge import Edge


class GraphNode(QGraphicsRectItem):
    """Contains the basic definition of a node. All other nodes share this baseclass."""
    def __init__(self, x, y):
        super().__init__(0, 0, 100, 100)
        self.setPos(x,y)
        # Node has a list of connected edges
        self.edge_list = []
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        # This specific ZValue is used so the nodes are rendered on top of the edges
        self.setZValue(1)
        self.name = ""

    def get_center(self):
        offset_x = self.rect().x() + self.rect().width() / 2
        offset_y = self.rect().y() + self.rect().height() / 2
        new_center = QPointF(self.pos().x() + offset_x, self.pos().y() + offset_y)
        return new_center

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.moveEdges(value)
        return QGraphicsRectItem.itemChange(self, change, value)

    def add_edge(self, edge: Edge, isSource: bool):
        self.edge_list.append((edge, isSource))

    def edges(self):
        return self.edge_list

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        rect = self.boundingRect()
        if self.isSelected():
            QPainter.drawRect(rect)

        QPainter.fillRect(rect, QBrush(Qt.lightGray))
        QPainter.drawText(rect, self.name)

    def moveEdges(self, new_pos):
        offset_x = self.rect().x() + self.rect().width()/2
        offset_y = self.rect().y() + self.rect().height()/2
        new_center = QPointF(new_pos.x() + offset_x, new_pos.y() + offset_y)
        for edge, isSource in self.edge_list:
            if isSource:
                # set source position to new center
                edge.set_source(new_center)
            else:
                # set target position to new center
                edge.set_dest(new_center)

class InNode(GraphNode):
    def __init__(self, x, y, model):
        super().__init__(x, y)
        self.name = "Input"
        self.model = model

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent, **kwargs):
        dialog = InputSettingsDialog(self.model)
        dialog.exec_()
        print("clicked: Input")

class OutNode(GraphNode):
    def __init__(self, x, y, model):
        super().__init__(x, y)
        self.name = "Output"
        self.model = model

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        dialog = OutputSettingsDialog(self.model)
        dialog.exec_()

class OrganNode(GraphNode):
    def __init__(self, organ, controller):
        super().__init__(*organ.pos)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.organ = organ
        self.controller = controller
        self.name = organ.get_name()

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent, **kwargs):
        dialog = OrganSettingsDialog(self.organ, self.controller)
        dialog.exec_()
        print("clicked: " + self.organ.get_name())


