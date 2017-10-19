from PyQt5.QtWidgets import QGraphicsScene

from gui.dialogs import NewNodeDialog
from gui.node import GraphNode


class GraphScene(QGraphicsScene):
    def __init__(self, *__args):
        super().__init__(*__args)

    def mouseDoubleClickEvent(self, mouse_event, **kwargs):
        pos = mouse_event.scenePos()

        self.dialog = NewNodeDialog()
        if self.dialog.exec_():
            text = self.dialog.nameField.text()
            self.addItem(GraphNode(pos.x(), pos.y(), text))
