from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem

from gui.dialogs import OrganSettingsDialog


class GraphNode(QGraphicsRectItem):
    def __init__(self, x: int, y: int, text: str):
        super().__init__(x, y, 100, 100)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.text = text
        
    def mousePressEvent(self, mouse_event, **kwargs):
        dialog = OrganSettingsDialog()
        print("clicked: " + self.text)

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        rect = self.boundingRect()
        if self.isSelected():
            QPainter.drawRect(rect)

        QPainter.fillRect(rect, QBrush(Qt.lightGray))
        QPainter.drawText(rect, self.text)

class OrganNode(QGraphicsRectItem):
    def __init__(self, organ, x, y):
        super().__init__(x, y, 100, 100)
        self.organ = organ
        print(organ)

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        rect = self.boundingRect()
        if self.isSelected():
            QPainter.drawRect(rect)

        QPainter.fillRect(rect, QBrush(Qt.lightGray))
        QPainter.drawText(rect, self.organ.get_name())
        for item in self.organ.get_vars():
            QPainter.drawText(rect, item)

