import ElementStyles
from ContentPages.ClassPage import Page
from ClassDBInterface import DBInterface
from UIElements import ButtonElement
from UIElements import ListElement
from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont, QPixmap
import io
import os

drive_letter = "C:"
main_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\"
learning_system_dir = os.path.join(main_dir, "Learning System")
e_packs_dir = os.path.join(main_dir, "Exercise Packs")

class CategoryPage(Page):
    ui = None
    exercises = None
    exercise_stats = None



    def __init__(self, ui):
        Page.__init__(self, "Category Page", 1)
        self.ui = ui
        self.initUI()


    def initUI(self):
        pass

    def objectReferences(self, db_interface, learning_page):
        self.db_interface = db_interface
        self.learning_page = learning_page
        self.categories = self.db_interface.fetchEntries("Categories", [])

    def showPage(self):
        self.setCategoryGrid()
        self.ui.content_pages.setCurrentIndex(self.page_number)

    def setCategoryGrid(self):
        count = len(self.categories)
        if count % 5 == 0:
            rows = int(count / 5)
        else:
            rows = int(count / 5) + 1
        for i in range(rows):
            if int(count / ((i + 1) * 5)) > 0:
                columns = 5
            elif i > 0:
                columns = count % (i * 5)
            else:
                columns = count
            for j in range(columns):
                index = i * 5 + j
                cat_str = self.categories[index]["ID"]
                button = QPushButton(cat_str)
                button.resize(150, 50)
                button.setStyleSheet("background-color : white")
                button.clicked.connect(lambda state, cat_str=button.text(): self.learning_page.showPage(cat_str))
                self.ui.cat_grid.addWidget(button, i, j)


