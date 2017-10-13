import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QDockWidget, QToolBar, QListWidget, QAction, \
    QFileDialog, QHBoxLayout, QWidget, QGridLayout, QSlider, QPushButton


class modelWindow(QMainWindow):

    def opendb(self):
        qfd = QFileDialog()
        qfd.setNameFilter("*.json")
        qfd.exec_()
        # We can only select a single file, therefore, we can always look at [0] without missing anything
        if self.controller.setdb(qfd.selectedFiles()[0]):
            self.statusBar().showMessage("Successfully loaded " + qfd.selectedFiles()[0])
        else:
            self.statusBar().showMessage("Problems loading " + qfd.selectedFiles()[0])

    def __init__(self, controller):
        super(modelWindow, self).__init__()
        self.controller = controller
        tb = QToolBar()
        tb.addAction(self.createAction("Load DB file", self.opendb))
        self.addToolBar(tb)

        logDockWidget = QDockWidget("Log", self)
        logDockWidget.setObjectName("LogDockWidget")
        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
                                      Qt.RightDockWidgetArea)
        self.listWidget = QListWidget()
        logDockWidget.setWidget(self.listWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidget)

        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.imageLabel.setPixmap(QPixmap("img.jpg"))

        self.controls = QGridLayout()

        BWsld = QSlider(Qt.Horizontal)
        BWlab = QLabel("Body Weight")
        self.controls.addWidget(BWlab, 0, 0)
        self.controls.addWidget(BWsld, 0, 1)
        BWsld.setObjectName("BodyWeight")
        BWsld.valueChanged.connect(self.globalSliderChange)

        GLUsld = QSlider(Qt.Horizontal)
        GLUlab = QLabel("Arterial Glucose Concentration")
        self.controls.addWidget(GLUlab, 1, 0)
        self.controls.addWidget(GLUsld, 1, 1)
        GLUsld.setObjectName("GluConArt")
        GLUsld.valueChanged.connect(self.globalSliderChange)

        LACsld = QSlider(Qt.Horizontal)
        LAClab = QLabel("Arterial Lactate Concentration")
        self.controls.addWidget(LAClab, 2, 0)
        self.controls.addWidget(LACsld, 2, 1)
        LACsld.setObjectName("LacConArt")
        LACsld.valueChanged.connect(self.globalSliderChange)

        O2sld = QSlider(Qt.Horizontal)
        O2lab = QLabel("Arterial Oxygen Concentration")
        self.controls.addWidget(O2lab, 3, 0)
        self.controls.addWidget(O2sld, 3, 1)
        O2sld.setObjectName("OxConArt")
        O2sld.valueChanged.connect(self.globalSliderChange)

        CO2sld = QSlider(Qt.Horizontal)
        CO2lab = QLabel("Arterial Carbon Dioxide Concentration")
        self.controls.addWidget(CO2lab, 4, 0)
        self.controls.addWidget(CO2sld, 4, 1)
        CO2sld.setObjectName("CO2ConArt")
        CO2sld.valueChanged.connect(self.globalSliderChange)

        FFAsld = QSlider(Qt.Horizontal)
        FFAlab = QLabel("Arterial FFA Concentration")
        self.controls.addWidget(FFAlab, 5, 0)
        self.controls.addWidget(FFAsld, 5, 1)
        FFAsld.setObjectName("FFAConArt")
        FFAsld.valueChanged.connect(self.globalSliderChange)

        organLayout = QGridLayout()

        Owesld = QSlider(Qt.Horizontal)
        Owslab = QLabel("Organ weight")
        organLayout.addWidget(Owslab, 0, 0)
        organLayout.addWidget(Owesld)

        organLayout.addWidget(QPushButton("Testbutton"))
        self.controls.addLayout(organLayout, 6, 0)

        centralLayout = QHBoxLayout()
        centralLayout.addWidget(self.imageLabel)
        centralLayout.addLayout(self.controls)
        centralWindow = QWidget()
        centralWindow.setLayout(centralLayout)

        self.opendb()
        self.setCentralWidget(centralWindow)
        self.setWindowState(Qt.WindowMaximized)
        self.showFullScreen()

    def globalSliderChange(self):
        print(self.sender().objectName() + "::" + str(self.sender().value()))
        self.controller.globalSliderChanged(self.sender())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
        action.setStatusTip(tip)
        if slot is not None:
            action.__getattr__(signal).connect(slot)
        if checkable:
            action.setCheckable(True)
        return action


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = modelWindow()
    sys.exit(app.exec_())