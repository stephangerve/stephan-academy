from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from ContentPages.ClassPage import Page

class TestPage(Page):
    def __init__(self, content_pages):
        super().__init__(11)
        uic.loadUi('Resources/test.ui', self)
        self.content_pages = content_pages

    def mouseMoveEvent(self, event):
        pass
        pass