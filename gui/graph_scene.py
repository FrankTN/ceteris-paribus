from PyQt5.QtWidgets import QGraphicsScene

from gui.dialogs import NewNodeDialog
from gui.node import GraphNode, OrganNode, InNode
from model import Model


class GraphScene(QGraphicsScene):
    def __init__(self, model: Model, *__args):
        super().__init__(*__args)
        self.addItem(InNode(0, 400, model))
        self.load_from_model(model)

    def load_from_model(self, model):
        for organ in model.organs:
            self.addItem(OrganNode(organ))