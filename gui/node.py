""" Module containing the definitions of different node types. Currently, the Input and Output nodes are special, the
    other nodes should all contain Organ data."""
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QLinearGradient, QFont, QFontMetrics
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem

from gui.dialogs import OrganSettingsDialog, InputSettingsDialog, OutputSettingsDialog
from gui.edge import Edge

class GraphNode(QGraphicsRectItem):
    """ Contains the basic definition of a node. All other nodes share this baseclass."""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50)
        self.setPos(x,y)
        # Node has a list of connected edges
        self.edge_list = []
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # This specific ZValue is used so the nodes are rendered on top of the edges
        self.setZValue(1)
        self.color = Qt.green
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

    def boundingRect(self):
        fm = QFontMetrics(QFont("Arial", 13))
        text_size = fm.boundingRect(self.name)
        rect = self.rect()

        return QRectF(rect.x(), rect.y(), text_size.width() + 6, text_size.height() + 10)

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        QPainter.setFont(QFont("Arial", 13))
        rect = self.boundingRect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, self.color)
        gradient.setColorAt(1, Qt.white)

        QPainter.fillRect(rect, gradient)
        QPainter.drawText(rect, Qt.AlignCenter, self.name)

    def setColor(self, color):
        self.color = color


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
    def __init__(self, x, y, controller):
        super().__init__(x, y)
        self.name = "Input"
        self.controller = controller

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent, **kwargs):
        dialog = InputSettingsDialog(self.controller)
        self.controller.setContext()
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

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        self.setColor(Qt.darkGreen)
        self.controller.change_context(self.organ)
        print("clicked: " + self.organ.get_name())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if value == False:
                self.setColor(Qt.green)
        return GraphNode.itemChange(self, change, value)


