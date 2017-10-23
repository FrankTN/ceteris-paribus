from PyQt5.QtWidgets import QGraphicsScene

from gui.dialogs import NewNodeDialog
from gui.node import GraphNode, OrganNode
from model import Model


class GraphScene(QGraphicsScene):
    def __init__(self, model: Model, *__args):
        super().__init__(*__args)
        self.load_from_model(model)

    def mouseDoubleClickEvent(self, mouse_event, **kwargs):
        pos = mouse_event.scenePos()

        self.dialog = NewNodeDialog()
        if self.dialog.exec_():
            text = self.dialog.nameField.text()
            self.addItem(GraphNode(pos.x(), pos.y(), text))

    def load_from_model(self, model):
        for organ in model.organs:
            self.addItem(OrganNode(organ))
            print(organ)