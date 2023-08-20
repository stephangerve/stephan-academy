from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from ContentPages.ClassPage import Page

class TestPage(Page):
    def __init__(self):
        super().__init__(11)
        uic.loadUi('Resources/test.ui', self)

    def mouseMoveEvent(self, event):
        pass
        pass