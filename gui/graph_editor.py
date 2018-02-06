from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QDockWidget

from ceteris_paribus.gui.graph_scene import GraphScene
from ceteris_paribus.gui.sidepane import ContextPane

from ceteris_paribus.db import db_dumper
from ceteris_paribus.gui.dialogs.db_dialogs import save_db_dialog


class GraphWindow(QMainWindow):
    """This class represents the MainWindow as a whole. The main window contains a graph editor windw and a sidepanel,
        which contains buttons to interact with the system."""
    def __init__(self, view_controller, *__args):
        super().__init__(*__args)
        self.scene = GraphScene(view_controller)
        self.controller = view_controller

        # A grid foreground
        self.grid = True

        # Create upper toolbar with menu options
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')

        db_open_action = file_menu.addAction('Open file')
        db_open_action.setStatusTip('Select a file to use as a database')
        db_open_action.triggered.connect(self.open_new_db)

        db_save_action = file_menu.addAction('Save file')
        db_save_action.setStatusTip('Save file as a database for future usage')
        db_save_action.triggered.connect(self.save_db)

        self.undo_stack = view_controller.get_undo_stack()

        edit_menu = menubar.addMenu('Edit')
        undo_action = edit_menu.addAction('Undo')
        undo_action.setStatusTip('Undo previous action')
        undo_action.triggered.connect(self.undo_stack.undo)
        redo_action = edit_menu.addAction('Redo')
        redo_action.setStatusTip('Redo previous action')
        redo_action.triggered.connect(self.undo_stack.redo)

        self.statusBar().showMessage("Ready")

        # Create context pane and link it to the controller
        self.side_pane = QDockWidget()
        self.context = ContextPane(self.controller)
        self.side_pane.setWidget(self.context)
        self.side_pane.setAllowedAreas(Qt.RightDockWidgetArea)

        # Demonstrate the results from the input.

        self.addDockWidget(Qt.RightDockWidgetArea, self.side_pane)

        graphics = QGraphicsView(self.scene)
        self.setCentralWidget(graphics)
        self.showFullScreen()

    def reload(self):
        # This method is called by the view_controller after a successful update of the model
        self.setCentralWidget(QGraphicsView(self.scene))
        self.context.reload()
        self.side_pane.setWidget(self.context)

    def get_scene(self):
        return self.scene

    def toggleGrid(self):
        if self.grid:
            self.scene.setBackgroundBrush(QBrush(Qt.white))
            self.grid = False
        else:
            self.scene.setBackgroundBrush(QBrush(Qt.lightGray, Qt.CrossPattern))
            self.grid = True

    def keyPressEvent(self, e):
        # Currently, we respond to a press of the Escape key by closing the program.
        if e.key() == Qt.Key_Escape:
            self.close()

    def open_new_db(self):
        self.controller.open_new_db()

    def save_db(self):
        target = save_db_dialog()
        db_dumper.dump_model(self.controller.model, target)