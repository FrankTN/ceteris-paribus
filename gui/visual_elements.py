""" Module containing the definitions of the parts of the graph, including node types and edges. Currently, the Input
    and Output nodes are special, the other nodes should all contain Organ data."""
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QLinearGradient, QFont, QFontMetrics, QColor, QPainterPath
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsLineItem, QSlider, QMessageBox

from ceteris_paribus.gui.dialogs.name_dialog import NameDialog


class GraphNode(QGraphicsRectItem):
    """ Contains the basic definition of a node. A node is a visual element on the graph scene represented by a colored
        box with a name. All other nodes share this baseclass."""

    def __init__(self, controller, x, y):
        super().__init__(x, y, 50, 50)
        self.controller = controller
        self.setPos(x, y)

        self.setAcceptDrops(True)
        # Node has a list of connected edges
        self.edge_list = []
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # This specific ZValue is used so the nodes are rendered on top of the edges
        self.setZValue(1)
        self.color = Qt.gray
        self.name = ""
        self.color_val_text = ""

    def dragEnterEvent(self, event):
        print("Entered drag")

    def get_center(self):
        # Find the center of the current node
        offset_x = self.rect().x() + self.rect().width() / 2
        offset_y = self.rect().y() + self.rect().height() / 2
        new_center = QPointF(self.pos().x() + offset_x, self.pos().y() + offset_y)
        return new_center

    def itemChange(self, change, value):
        # Overrides the itemChange function of the RectItem in such a way that the edges are moved if the item itself is
        # moved
        if change == QGraphicsItem.ItemPositionChange:
            self.moveEdges(value)
        return QGraphicsRectItem.itemChange(self, change, value)

    def add_edge(self, edge, isSource):
        # Add edge to the local list of edges
        self.edge_list.append((edge, isSource))

    def remove_output_edge(self):
        for edge, isSource in self.edge_list:
            if not isSource:
                self.edge_list.remove((edge, isSource))

    def get_edges(self):
        return self.edge_list

    def boundingRect(self):
        # Reimplementation of the boundingRect function, to resize the node based on the length of its title
        fm = QFontMetrics(QFont("Arial", 15))
        text_size = fm.boundingRect(self.name + self.color_val_text)
        rect = self.rect()
        new_width = max(text_size.width(), rect.width())
        new_height = text_size.height()
        return QRectF(rect.x(), rect.y(), new_width + 6, new_height + 10)

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        # The basic paint method, draws a box with a gradient and fills it with the title
        QPainter.setFont(QFont("Arial", 15))
        rect = self.boundingRect()
        QPainter.drawRect(rect)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, self.color)
        gradient.setColorAt(1, Qt.white)

        QPainter.fillRect(rect, gradient)
        QPainter.drawText(rect, Qt.AlignCenter, self.name + " " + self.color_val_text)

    def shape(self):
        # This method must be overridden for the textboxes to be selectable after changing the names
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def set_color(self, range, gradient_table):
        # Sets the color of the node based on a range of values. Range is a list with three elements, [min, max, val].
        # Based on the distance of val from the maximum, we give the node a color. This allows the user to get an
        # overview of the space left to move a certain variable
        range_min = range[0]
        range_max = range[1]
        val = range[2]
        normalized_val = (val - range_min) / (range_max - range_min)
        index = int(normalized_val * len(gradient_table))

        self.color_val_text = str(round(val, 2))
        # Here, we use the index to find the closest color in the gradient table.
        self.color = QColor(*gradient_table[index])

    def set_gray(self):
        # The default color
        self.color = Qt.gray
        self.color_val_text = ""

    def set_dark_gray(self):
        # The default color when an object is selected
        self.color = Qt.darkGray

    def moveEdges(self, new_pos):
        # This function moves the edges in the pane to follow the node
        offset_x = self.rect().x() + self.rect().width() / 2
        offset_y = self.rect().y() + self.rect().height() / 2
        new_center = QPointF(new_pos.x() + offset_x, new_pos.y() + offset_y)
        for edge, isSource in self.edge_list:
            if isSource:
                # set source position to new center
                edge.set_source(new_center)
            else:
                # set target position to new center
                edge.set_dest(new_center)


class InNode(GraphNode):
    # TODO expand functionality
    def __init__(self, x, y, controller):
        super().__init__(controller, x, y)
        self.name = "Input"
        self.controller = controller


class OutNode(GraphNode):
    # TODO expand functionality
    def __init__(self, x, y, controller):
        super().__init__(controller, x, y)
        self.name = "Output"
        self.controller = controller


class OrganNode(GraphNode):
    # Subclass for the organ nodes
    def __init__(self, organ, controller):
        super().__init__(controller, *organ.pos)
        self.click = False
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.organ = organ
        self.controller = controller
        self.name = organ.get_name()

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        self.controller.change_context_organ(self.organ)
        print("clicked: " + self.organ.get_name())
        self.click = True

    def mouseDoubleClickEvent(self, event):
        dialog = NameDialog()

        if dialog.exec():
            name = dialog.get_name()
            if name not in self.controller.get_organ_names():
                self.organ.set_name(name)
                self.name = name
                self.controller.change_context_organ(self.organ)
                self.controller.ui.reload()
            else:
                msg = QMessageBox()
                msg.setText("Warning: name already in use")
                msg.exec()


class Edge(QGraphicsLineItem):
    """ This class contains the definition of an edge in the graph."""

    def __init__(self, source_node, dest_node):
        super().__init__(source_node.get_center().x(), source_node.get_center().y(), dest_node.get_center().x(),
                         dest_node.get_center().y())
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source_node = source_node
        self.dest_node = dest_node
        source_node.add_edge(self, True)
        dest_node.add_edge(self, False)
        self.arrow_size = 10

    def get_source(self):
        return self.source_node

    def get_dest(self):
        return self.dest_node

    def set_source(self, new_position):
        self.setLine(new_position.x(), new_position.y(), self.dest_node.get_center().x(),
                     self.dest_node.get_center().y())
        self.update()

    def set_dest(self, new_position):
        self.setLine(self.source_node.get_center().x(), self.source_node.get_center().y(),
                     new_position.x(), new_position.y())

        self.dest_point = new_position
        self.update()

    def __str__(self):
        return "Source: [" + self.source_node.name + "] Dest: [" + self.dest_node.name + "]"


class FloatSlider(QSlider):
    """ Custom QSlider subclass which performs a translation step between its value in a range from [0,100] to the
        variables arbitrary floating point range."""

    def __init__(self, min, max, val, target):
        super().__init__(Qt.Horizontal)
        self.diff = float(max) - float(min)
        self.min = float(min)

        # This is the function hook we will call once we have rescaled the value
        self.target = target
        self.setRange(0, 100)
        self.setSingleStep(1)

        if self.diff == 0:
            # We have no range to map to, defaulting to 0
            scaled_init_val = 0
        else:
            scaled_init_val = (float(val) - float(min)) * 100 / self.diff
        self.setValue(scaled_init_val)
        self.valueChanged.connect(self.value_handler)

    def value_handler(self, value):
        if self.diff == 0:
            # We have no range to map to, defaulting to 0
            scaled_val = 0
        else:
            scaled_val = ((value / 100) * self.diff) + self.min
        self.target(scaled_val)


def print_warning(text):
    msg = QMessageBox()
    msg.setWindowTitle("Warning")
    msg.setText(text)
    msg.exec()
