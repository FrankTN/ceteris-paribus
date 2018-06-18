""" This module contains the commands issued by the GUI. Every command is a subclass of QUndoCommand. This allows for
    undoing the command.
"""
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QUndoCommand


class MoveCommand(QUndoCommand):
    """ This class specifies what happens when a move command is performed. It stores the old position so that the
        action may be undone."""

    def __init__(self, controller, node, old_pos):
        super().__init__()
        self.controller = controller
        self.node = node
        self.old_pos = old_pos
        self.new_pos = node.scenePos()

    def undo(self):
        self.node.setPos(self.old_pos)

    def redo(self):
        self.node.setPos(self.new_pos)


class DeleteCommand(QUndoCommand):
    """ This class specifies the data required to undo a delete action. If we undo the action the action the organ
        is restored in the model, together with its edges."""

    def __init__(self, controller, organ):
        super().__init__()
        self.controller = controller
        self.organ = organ
        self.edge_list = controller.ui.scene.get_edges_for_organ(organ)

    def redo(self):
        self.controller.remove_organ(self.organ)

    def undo(self):
        pos = QPointF(self.organ.get_pos()[0], self.organ.get_pos()[1])
        name = self.organ.get_name()
        variables = self.organ.get_local_ranges()
        funcs = self.organ.get_funcs()
        edge_src_list = []
        for edge in self.edge_list:
            if not edge[1]:
                edge_src_list.append(edge[0].get_source())
        self.controller.add_organ(pos, name, variables, funcs, edge_src_list)


class NewCommand(QUndoCommand):
    """ If we undo the NewCommand we remove a node"""

    def __init__(self, controller, pos, dialog, source_nodes):
        super().__init__()
        self.controller = controller
        self.pos = pos
        self.dialog = dialog
        self.sources = source_nodes

    def redo(self):
        dialog = self.dialog
        self.organ = self.controller.add_organ(self.pos, dialog.get_name(), dialog.get_variables(), dialog.get_funcs(),
                                               self.sources)

    def undo(self):
        self.controller.remove_organ(self.organ)
