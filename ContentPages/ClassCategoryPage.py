from PyQt5 import uic
import ElementStyles
from ContentPages.ClassPage import Page
from ClassDBInterface import DBInterface
from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QCursor
import io
import os
import Config

drive_letter = "C:"
main_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\"
learning_system_dir = os.path.join(main_dir, "Learning System")
e_packs_dir = os.path.join(main_dir, "Exercise Packs")

class CategoryPage(Page):
    exercises = None
    exercise_stats = None



    def __init__(self, content_pages):
        Page.__init__(self, Config.CategoryPage_page_number)
        uic.loadUi('Resources/UI/categories_page.ui', self)
        self.content_pages = content_pages
        self.initUI()


    def initUI(self):
        pass

    def objectReferences(self, db_interface, learning_page, categories):
        self.db_interface = db_interface
        self.learning_page = learning_page
        self.categories = categories
        self.setCategoryGrid()

    def showPage(self):
        self.content_pages.setCurrentIndex(self.page_number)

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
                cat_str = self.categories[index]["Category"]
                button = QPushButton(cat_str)
                button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                #button.resize(150, 100)
                #button.setStyleSheet("background-color : white")
                button.setStyleSheet("color : black")
                button.setFlat(True)
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(button)
                frame = QFrame()
                frame.setLayout(layout)
                ElementStyles.regularShadow(frame)
                ElementStyles.hoverEffect(frame)
                button.clicked.connect(lambda state, cat_str=button.text(): self.learning_page.showPage(cat_str))
                self.cat_grid.addWidget(frame, i, j)


