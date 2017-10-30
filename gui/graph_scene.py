from PyQt5.QtWidgets import QGraphicsScene, QWidget, QGridLayout, QLabel

from gui.dialogs import NewNodeDialog
from gui.edge import Edge
from gui.node import GraphNode, OrganNode, InNode
from model import Model


class GraphScene(QGraphicsScene):
    def __init__(self, model: Model, *__args):
        super().__init__(*__args)
        self.input_node = InNode(0, 400, model)
        self.addItem(self.input_node)
        self.load_from_model(model)

    def load_from_model(self, model):
        for organ in model.organs.values():
            node = OrganNode(organ)
            self.addItem(node)
            self.addItem(Edge(self.input_node, node))

class ResultPane(QWidget):
    def __init__(self, model):
        super().__init__()
        layout = QGridLayout()
        self.model = model
        for index, varname in enumerate(self.model.get_outputs()):
            print(varname, self.model.get_outputs[varname])
            layout.addWidget(QLabel(varname), index, 0)
            layout.addWidget(QLabel(str(self.model.get_outputs[varname])), index, 1)
        self.setLayout(layout)

