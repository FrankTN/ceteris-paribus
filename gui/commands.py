""" This module contains the commands issued by the GUI. Every command is a subclass of QUndoCommand. This allows for
    undoing the command.
"""
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QUndoCommand


class MoveCommand(QUndoCommand):
    def __init__(self, *__args):
        super().__init__(*__args)


class DeleteCommand(QUndoCommand):
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
        self.controller.add_organ(pos, name, variables, funcs, self.edge_list)