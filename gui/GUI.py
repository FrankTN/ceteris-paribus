""" This class represents the main window in the user interface. Through a connection to the controller, it
    communicates with the model."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QDockWidget, QToolBar, QListWidget, QAction, \
    QFileDialog, QHBoxLayout, QWidget, QGridLayout, QSlider, QPushButton, QSizePolicy, QComboBox, QPlainTextEdit


class modelWindow(QMainWindow):

    def open_db(self):
        """ This function, which opens the database and connects it to the model is called before the UI can actually be
            used. """
        qfd = QFileDialog()
        qfd.setNameFilter("*.json")
        qfd.exec_()
        # We can only select a single file, therefore, we can always look at [0] without missing anything
        if self.controller.set_db(qfd.selectedFiles()[0]):
            self.statusBar().showMessage("Successfully loaded " + qfd.selectedFiles()[0])
        else:
            self.statusBar().showMessage("Problems loading " + qfd.selectedFiles()[0])

    def __init__(self, controller):
        super(modelWindow, self).__init__()
        self.controller = controller
        self.open_db()
        self.init_UI()

    def init_UI(self):
        # Create upper toolbar with menu options
        tb = QToolBar()
        tb.addAction(self.create_action("Load DB file", self.open_db))
        self.addToolBar(tb)

        # Create log which will eventually show program logging outputs
        logDockWidget = QDockWidget("Log", self)
        logDockWidget.setObjectName("LogDockWidget")
        logDockWidget.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.listWidget = QListWidget()
        logDockWidget.setWidget(self.listWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, logDockWidget)

        # Create a statusbar, which will display context-dependent messages
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

        # Fill the left region of the screen with a placeholder image TODO replace by actual model view
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.imageLabel.setPixmap(QPixmap("img.jpg"))

        # Create controls and add sliders for the entire body
        self.controls = QGridLayout()

        BWsld = QSlider(Qt.Horizontal)
        BWlab = QLabel("Body Weight")
        self.controls.addWidget(BWlab, 0, 0)
        self.controls.addWidget(BWsld, 0, 1)
        BWsld.setObjectName("BodyWeight")
        BWsld.valueChanged.connect(self.global_slider_change)

        GLUsld = QSlider(Qt.Horizontal)
        GLUlab = QLabel("Arterial Glucose Concentration")
        self.controls.addWidget(GLUlab, 1, 0)
        self.controls.addWidget(GLUsld, 1, 1)
        GLUsld.setObjectName("GluConArt")
        GLUsld.valueChanged.connect(self.global_slider_change)

        LACsld = QSlider(Qt.Horizontal)
        LAClab = QLabel("Arterial Lactate Concentration")
        self.controls.addWidget(LAClab, 2, 0)
        self.controls.addWidget(LACsld, 2, 1)
        LACsld.setObjectName("LacConArt")
        LACsld.valueChanged.connect(self.global_slider_change)

        O2sld = QSlider(Qt.Horizontal)
        O2lab = QLabel("Arterial Oxygen Concentration")
        self.controls.addWidget(O2lab, 3, 0)
        self.controls.addWidget(O2sld, 3, 1)
        O2sld.setObjectName("OxConArt")
        O2sld.valueChanged.connect(self.global_slider_change)

        CO2sld = QSlider(Qt.Horizontal)
        CO2lab = QLabel("Arterial Carbon Dioxide Concentration")
        self.controls.addWidget(CO2lab, 4, 0)
        self.controls.addWidget(CO2sld, 4, 1)
        CO2sld.setObjectName("CO2ConArt")
        CO2sld.valueChanged.connect(self.global_slider_change)

        FFAsld = QSlider(Qt.Horizontal)
        FFAlab = QLabel("Arterial FFA Concentration")
        self.controls.addWidget(FFAlab, 5, 0)
        self.controls.addWidget(FFAsld, 5, 1)
        FFAsld.setObjectName("FFAConArt")
        FFAsld.valueChanged.connect(self.global_slider_change)

        # Create labels showing global values in the body
        global_val_layout = QGridLayout()

        oxconlbl = QLabel("Whole body oxygen consumption")
        self.oxconval = QLabel("000.00")
        self.oxconval.setFixedSize(self.oxconval.sizeHint())
        self.oxconval.setStyleSheet("background: white")

        spec_o2_lbl = QLabel("Whole body specific oxygen concentration")
        self.spec_o2_val = QLabel("000.00")
        self.spec_o2_val.setFixedSize(self.oxconval.sizeHint())
        self.spec_o2_val.setStyleSheet("background: white")

        spec_co2_lbl = QLabel("Whole body specific CO2 concentration")
        self.spec_co2_val = QLabel("000.00")
        self.spec_co2_val.setFixedSize(self.oxconval.sizeHint())
        self.spec_co2_val.setStyleSheet("background: white")

        co2prodlbl = QLabel("Whole body carbon dioxide production")
        self.co2prodval = QLabel("000.00")
        self.co2prodval.setFixedSize(self.oxconval.sizeHint())
        self.co2prodval.setStyleSheet("background: white")

        rqprodlbl = QLabel("Whole body respiratory quotient")
        self.rqval = QLabel("00.00")
        self.rqval.setFixedSize(self.oxconval.sizeHint())
        self.rqval.setStyleSheet("background: white")



        global_val_layout.addWidget(oxconlbl, 0, 0)
        global_val_layout.addWidget(self.oxconval, 0, 1)
        global_val_layout.addWidget(spec_o2_lbl, 1, 0)
        global_val_layout.addWidget(self.spec_o2_val, 1, 1)
        global_val_layout.addWidget(spec_co2_lbl, 2, 0)
        global_val_layout.addWidget(self.spec_co2_val, 2, 1)
        global_val_layout.addWidget(co2prodlbl, 3, 0)
        global_val_layout.addWidget(self.co2prodval, 3, 1)
        global_val_layout.addWidget(rqprodlbl, 4, 0)
        global_val_layout.addWidget(self.rqval, 4, 1)
        frame = QFrame()
        frame.setLayout(global_val_layout)

        self.controls.addWidget(frame, 7, 0)

        # Create layout with organ controls.
        self.organ_layout = QGridLayout()

        Owesld = QSlider(Qt.Horizontal)
        Owslab = QLabel("Organ weight")
        self.organ_layout.addWidget(Owslab, 0, 0)
        self.organ_layout.addWidget(Owesld)

        organ_selector = QComboBox()
        organ_selector.addItems(self.controller.get_organ_names())
        organ_selector.currentIndexChanged.connect(self.select_organ)
        self.organ_layout.addWidget(organ_selector, 3, 0, 2, 1)
        self.organ_volume = QPlainTextEdit()
        self.organ_volume.setReadOnly(True)
        self.organ_layout.addWidget(self.organ_volume)

        # This fills out the other values in the organ selection form. We have to send the signal manually once, as the
        # index has not yet changed.
        self.select_organ(organ_selector.currentIndex())

        self.controls.addLayout(self.organ_layout, 6, 0, 1, 2)

        # Finally, create a HBox and add the other components to it. Then, set it as the central widget.
        centralLayout = QHBoxLayout()
        centralLayout.addWidget(self.imageLabel)
        centralLayout.addLayout(self.controls)
        centralWindow = QWidget()
        centralWindow.setLayout(centralLayout)

        self.setCentralWidget(centralWindow)
        self.setWindowState(Qt.WindowMaximized)
        self.showFullScreen()

    def global_slider_change(self):
        # This method delegates the changing of a global value to the controller.
        print(self.sender().objectName() + "::" + str(self.sender().value()))
        self.controller.global_slider_changed(self.sender())

    def keyPressEvent(self, e):
        # Currently, we respond to a press of the Escape key by closing the program.
        if e.key() == Qt.Key_Escape:
            self.close()

    def set_global_VO2(self, newVO2):
        self.oxconval.setText(str(newVO2))

    def set_global_VCO2(self, newVCO2):
        self.co2prodval.setText(str(newVCO2))

    def set_spec_VO2(self, newsVO2):
        self.spec_o2_val.setText(str(newsVO2))

    def set_spec_VCO2(self, newsVCO2):
        self.spec_co2_val.setText(str(newsVCO2))

    def set_global_RQ(self, newRQ):
        self.rqval.setText(str(newRQ))

    def create_action(self, text, slot=None, shortcut=None, icon=None,
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

    def select_organ(self, new_organ):
        organ = self.controller.get_organ(new_organ)
        self.organ_volume.setPlainText(str(organ.get_volume()))
        print(organ)
