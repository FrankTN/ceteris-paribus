import sys
from multiprocessing import Queue
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QTextEdit, QPushButton, QWidget

class WriteStream(object):
    def __init__(self, queue, color = None):
        self.queue = queue
        self.color = color

    def write(self, text):
        self.queue.put(text)

# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal
class Receiver(QObject):
    stdout_signal = pyqtSignal(str)

    def __init__(self,queue,*args,**kwargs):
        QObject.__init__(self,*args,**kwargs)
        self.queue = queue

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.stdout_signal.emit(text)


