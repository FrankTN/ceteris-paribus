import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QApplication, QDockWidget, QToolBar, QAction, QMenu

from gui.dialogs import NewNodeDialog
from gui.graph_scene import GraphScene, ResultPane


class graphWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.scene = GraphScene(controller)
        self.controller = controller

        # a grid foreground
        self.scene.setBackgroundBrush(QBrush(Qt.lightGray, Qt.CrossPattern))
        self.grid = True

        menu_bar = QToolBar()

        open_file = QAction("Open file")
        open_file.setStatusTip("Select a file to load a new model")
        open_file.triggered.connect(self.open_new_db)

        menu_bar.addAction(open_file)
        self.addToolBar(menu_bar)

        self.statusBar().showMessage("Ready")

        result_pane = QDockWidget()
        result_pane.setWidget(ResultPane(controller.get_model()))
        result_pane.setAllowedAreas(Qt.RightDockWidgetArea)

        # Demonstrate the results from the input.

        self.addDockWidget(Qt.RightDockWidgetArea, result_pane)

        graphics = QGraphicsView(self.scene)
        self.setCentralWidget(graphics)
        self.showFullScreen()

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
        self.setCentralWidget(GraphScene(self.controller.get_model()))