from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsScene

from gui.dialogs import NewNodeDialog
from gui.visual_elements import OrganNode, InNode, OutNode, Edge


class GraphScene(QGraphicsScene):
    """The GraphScene class is used to display the visual elements in a grid."""
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
        # Creates a scene based on a model object
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

    def add_organ_node(self, organ, edge_src_list):
        # Create a new node representing an organ
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

    def remove_organ_node(self, organ):
        # Remove an organ node from the model
        to_be_removed = self.items[organ.get_name()]
        for edge in self.edges:
            if edge.get_source() is to_be_removed or edge.get_dest() is to_be_removed:
                self.removeItem(edge)
        self.removeItem(to_be_removed)

    def mouseDoubleClickEvent(self, event):
        # Override what happens on double clicking inside the graphscene. The item variable is None if there is no item
        # at the position of the mouseclick
        item = self.itemAt(event.scenePos().x(), event.scenePos().y(), QTransform())
        if item:
            item.mouseDoubleClickEvent(event)
        else:
            self.create_new_node(event.scenePos())

    def create_new_node(self, pos):
        dialog = NewNodeDialog(self.controller)
        if dialog.exec_():
            print(dialog.get_variables())
            organ = self.controller.add_organ_node(pos, dialog.get_name(), dialog.get_variables(), dialog.get_funcs())
            self.add_organ_node(organ, dialog.get_edge_item())
