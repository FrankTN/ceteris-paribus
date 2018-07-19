"""This module contains the class for the main window of the application."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QDockWidget, QMessageBox

from ceteris_paribus.gui.graph_scene import GraphScene
from ceteris_paribus.gui.sidepane import ContextPane

from ceteris_paribus.db import db_dumper
from ceteris_paribus.gui.dialogs.db_dialogs import save_db_dialog
import errno


class GraphWindow(QMainWindow):
    """This class represents the MainWindow as a whole. The main window contains a graph editor windw and a sidepanel,
        which contains buttons to interact with the system."""

    def __init__(self, view_controller, *__args):
        super().__init__(*__args)
        self.scene = GraphScene(view_controller)
        self.controller = view_controller

        # A grid foreground
        self.grid = False

        # Create upper toolbar with menu options
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')

        new_project_action = file_menu.addAction('New project')
        new_project_action.setStatusTip('Initialize a new project')
        new_project_action.triggered.connect(self.new_project)

        db_open_action = file_menu.addAction('Open project')
        db_open_action.setStatusTip('Select a file to use as a database')
        db_open_action.triggered.connect(self.open_new_db)

        db_save_action = file_menu.addAction('Save project')
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

        view_menu = menubar.addMenu('View')
        grid_action = view_menu.addAction('Toggle grid')
        grid_action.setStatusTip('Show or hide the grid background')
        grid_action.triggered.connect(self.toggleGrid)

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
        self.reload_context()

    def reload_context(self):
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

    def new_project(self):
        organs = self.controller.global_control.model_control.get_model().get_organs()
        if organs:
            msg = QMessageBox()
            msg.setText("Save current model first?")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            ret = msg.exec_()
            if ret == QMessageBox.Cancel:
                return
            elif ret == QMessageBox.Save:
                self.save_db()
            self.controller.global_control.new_model(None)
            # Reset the main Scene
            self.scene = GraphScene(self.controller)
            # Reset the context pane
            self.context = ContextPane(self.controller)
            self.reload()

    def save_db(self):
        # View controller
        if len(self.controller.get_organs()) > 0:
            target = save_db_dialog()
            try:
                db_dumper.dump_model(self.controller.get_model(), target)
            except OSError as err:
                if err.errno == errno.EACCES:
                    msg = QMessageBox()
                    msg.setWindowTitle("Error")
                    msg.setText("Permission denied, please try another location")
                    msg.exec_()
                    self.save_db()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("A model has not yet been defined, please add at least one organ")
            msg.exec_()
