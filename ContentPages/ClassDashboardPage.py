from PyQt5 import uic
from ContentPages.ClassPage import Page
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
import Config

class DashboardPage(Page):


    def __init__(self, content_pages):
        Page.__init__(self, Config.DashboardPage_page_number)
        uic.loadUi('Resources/UI/dashboard_page.ui', self)
        self.content_pages = content_pages


    def referenceObjects(self):
        pass


    def showPage(self):
        self.content_pages.setCurrentIndex(self.page_number)