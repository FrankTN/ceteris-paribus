from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsScene, QWidget, QGridLayout, QLabel

from gui.dialogs import NewNodeDialog
from gui.edge import Edge
from gui.node import OrganNode, InNode, OutNode


class GraphScene(QGraphicsScene):
    def __init__(self, controller, *__args):
        super().__init__(*__args)
        self.controller = controller
        self.input_node = InNode(0, 400, controller)
        self.addItem(self.input_node)
        self.output_node = OutNode(600, 400, controller)
        self.addItem(self.output_node)
        self.load_from_model(controller.get_model())

    def load_from_model(self, model):
        for organ in model.organs.values():
            node = OrganNode(organ)
            self.addItem(node)
            self.addItem(Edge(self.input_node, node))
            self.addItem(Edge(node, self.output_node))

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.scenePos().x(), event.scenePos().y(), QTransform())
        if item:
            item.mouseDoubleClickEvent(event)
        else:
            self.create_new_node()

    def create_new_node(self):
        dialog = NewNodeDialog(self.controller)
        if dialog.exec_():
            pass

class ResultPane(QWidget):
    def __init__(self, model):
        super().__init__()
        layout = QGridLayout()
        self.model = model
        outputs = self.model.get_outputs()
        for index, varname in enumerate(outputs):
            print(varname, outputs[varname])
            layout.addWidget(QLabel(varname), index, 0)
            layout.addWidget(QLabel(str(outputs[varname])), index, 1)
        self.setLayout(layout)

