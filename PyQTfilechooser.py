import sys

import os
from PyQt5 import QtCore
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QMainWindow, QWidget, QFileSystemModel, QTreeView, QSplitter, QHBoxLayout, \
    QApplication

import main_script


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(400, 300)
        self.fileBrowserWidget = QWidget(self)
        self.setCentralWidget(self.fileBrowserWidget)
        self.setWindowTitle("Please specify database")

        self.dirmodel = QFileSystemModel()
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries)
        self.folder_view = QTreeView()
        self.folder_view.setModel(self.dirmodel)
        self.folder_view.clicked[QtCore.QModelIndex].connect(self.clicked)
        self.folder_view.setRootIndex(self.dirmodel.index(QDir.currentPath()))
        self.folder_view.setColumnWidth(0,200)

        self.folder_view.hideColumn(3)

        hbox = QHBoxLayout(self.fileBrowserWidget)
        hbox.addWidget(self.folder_view)

    def set_path(self, path):
        self.dirmodel.setRootPath(path)

    def clicked(self, index):
        # get selected path of folder_view
        index = self.folder_view.currentIndex()
        dir_path = self.dirmodel.filePath(index)
        main_script.load_db(dir_path)
        print(dir_path)

def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    main.set_path(os.getcwd())

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

