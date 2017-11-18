from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsScene, QWidget, QGridLayout, QLabel

from gui.dialogs import NewNodeDialog
from gui.edge import Edge
from gui.visual_elements import OrganNode, InNode, OutNode


class GraphScene(QGraphicsScene):
    def __init__(self, controller, *__args):
        super().__init__(*__args)
        self.controller = controller
        self.input_node = InNode(-300, 0, controller)
        self.addItem(self.input_node)
        self.output_node = OutNode(300, 0, controller)
        self.addItem(self.output_node)
        # Items is used as a dict to keep internal references to the items.
        self.items = {}
        self.items['Global Input'] = self.input_node
        self.edges = []
        self.load_from_model(controller.get_model())

    def load_from_model(self, model):
        for organ in model.organs.values():
            node = OrganNode(organ, self.controller)
            self.items[organ.get_name()] = node
            self.addItem(node)
            in_edge = Edge(self.input_node, node)
            self.addItem(in_edge)
            out_edge = Edge(node, self.output_node)
            self.addItem(out_edge)
            self.edges.append(in_edge)
            self.edges.append(out_edge)

    def add_organ(self, organ, edge_src_list):
        node = OrganNode(organ, self.controller)
        self.items[organ.get_name()] = node
        self.addItem(node)
        out_edge = Edge(node, self.output_node)
        self.addItem(out_edge)
        for source in edge_src_list:
            source_node = self.items[source.text()]
            in_edge = Edge(source_node, node)
            self.edges.append(in_edge)
            self.addItem(in_edge)
        self.edges.append(out_edge)

    def remove_organ(self, organ):
        to_be_removed = self.items[organ.get_name()]
        for edge in self.edges:
            if edge.get_source() is to_be_removed or edge.get_dest() is to_be_removed:
                self.removeItem(edge)
        self.removeItem(to_be_removed)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.scenePos().x(), event.scenePos().y(), QTransform())
        if item:
            item.mouseDoubleClickEvent(event)
        else:
            self.create_new_node(event.scenePos())

    def create_new_node(self, pos):
        dialog = NewNodeDialog(self.controller)
        if dialog.exec_():
            print(dialog.get_variables())
            organ = self.controller.add_organ(pos, dialog.get_name(), dialog.get_variables(), dialog.get_funcs())
            self.add_organ(organ, dialog.get_edge_item())
