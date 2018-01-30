class Controller(object):
    """ The controller contains the main function. It oversees program execution and provides an interface between the
        model and the User Interface."""

    def __init__(self):
        # Create an undo stack
        self.undo_stack = QUndoStack()