from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsPathItem

from gui.dialogs import OrganSettingsDialog, InputSettingsDialog


class GraphNode(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(x, y, 100, 100)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.name = ""

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            pass
        return QGraphicsRectItem.itemChange(self, change, value)



    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        rect = self.boundingRect()
        if self.isSelected():
            QPainter.drawRect(rect)

        QPainter.fillRect(rect, QBrush(Qt.lightGray))
        QPainter.drawText(rect, self.name)

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
        print(organ)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent, **kwargs):
        dialog = OrganSettingsDialog(self.organ)
        dialog.exec_()
        print("clicked: " + self.organ.get_name())

class Path(QGraphicsPathItem):
    def __init__(self, path, scene):
        super(Path, self).__init__(path)
        for i in range(path.elementCount()):
            node = GraphNode(self, i)
            node.setPos(QPointF(path.elementAt(i)))
            scene.addItem(node)
        self.setPen(QPen(Qt.red, 1.75))

    def updateElement(self, index, pos):
        path = self.path()
        path.setElementPositionAt(index, pos.x(), pos.y())
        self.setPath(path)

