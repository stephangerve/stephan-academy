from ContentPages.ClassPage import Page
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
import Config

class DashboardPage(Page):
    ui = None



    def __init__(self, ui):
        Page.__init__(self, Config.DashboardPage_page_number)
        self.ui = ui


    def referenceObjects(self):
        pass


    def showPage(self):
        self.ui.button_dashboard.setChecked(True)
        self.ui.button_dashboard.setEnabled(False)
        self.ui.button_dashboard.setStyleSheet("background-color: rgb(58, 74, 97); color: white")
        self.ui.button_dashboard.setCursor(QCursor(QtCore.Qt.ArrowCursor))
        pushbuttons = [self.ui.button_flashcards, self.ui.button_studylist, self.ui.button_learn]
        for button in pushbuttons:
            if button.isChecked():
                button.setChecked(False)
                button.setEnabled(True)
                button.setStyleSheet("background-color: #2A4D87; color: white")
                button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.ui.content_pages.setCurrentIndex(self.page_number)