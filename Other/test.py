import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QShortcut, QLabel, QApplication, QHBoxLayout, QMainWindow
from PyQt5 import uic
import Config

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Resources/ui_main.ui")
        self.ui.show()
        self.page = ActualPage(self.ui)



class Page(QWidget):
    def __init__(self):
        super().__init__()


class AnotherOne:
    def __init__(self):
        pass

    #@pyqtSlot()
    def on_open(self, dummy=None):
        dummy = "Opening!"
        print(dummy)

class ActualPage(Page):
    def __init__(self, ui):
        Page.__init__(self)
        self.ui = ui
        self.ao = AnotherOne()
        #self.label = QLabel("Try shortcut", self)
        self.shortcut = QShortcut(QKeySequence(Config.OP_SIMPLE), self.ui)
        self.shortcut.activated.connect(self.ao.on_open)

        # self.layout = QHBoxLayout()
        # self.layout.addWidget(self.label)
        #
        # self.setLayout(self.layout)
        # self.resize(150, 100)
        # self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())
