import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QLabel, QGraphicsView, QApplication, QSlider

from gui.graph_scene import GraphScene


class graphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = GraphScene()

        # a grid foreground
        self.scene.setBackgroundBrush(QBrush(Qt.lightGray, Qt.CrossPattern))
        self.grid = True

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    graph = graphWindow()
    sys.exit(app.exec_())