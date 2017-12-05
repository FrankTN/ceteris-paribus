from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform, QBrush
from PyQt5.QtWidgets import QGraphicsScene

from gui.commands import MoveCommand
from gui.dialogs import NewNodeCreator
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

        self.setBackgroundBrush(QBrush(Qt.lightGray, Qt.CrossPattern))

        self.load_from_model(controller.get_model())

    def get_edges_for_organ(self, organ):
        return self.items[organ.get_name()].get_edges()

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
        self.edges.append(out_edge)
        self.addItem(out_edge)
        # We need a copy because the original is being updated each time we create a new edge
        local_list = edge_src_list[:]
        for source in local_list:
            # We only add source edges for now
            in_edge = Edge(source, node)
            self.edges.append(in_edge)
            self.addItem(in_edge)

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

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos().x(), event.scenePos().y(), QTransform())
        if item:
            self.dragPos = item.scenePos()

        return QGraphicsScene.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        foundItem = self.itemAt(event.scenePos().x(), event.scenePos().y(), QTransform())
        if foundItem:
            move = MoveCommand(self.controller, foundItem, self.dragPos)
            self.controller.get_undo_stack().push(move)
            # handle drag and drop
        return QGraphicsScene.mouseReleaseEvent(self, event)

    def create_new_node(self, pos):
        dialog = NewNodeCreator(self.controller)

        if dialog.run():
            sources = dialog.get_sources()
            source_nodes = []
            for source_name in sources:
                corresponding_node = self.items[source_name]
                source_nodes.append(corresponding_node)
            self.controller.add_organ(pos, dialog.get_name(), dialog.get_variables(), dialog.get_funcs(), source_nodes)

    def update_model(self):
        # TODO implement
        pass