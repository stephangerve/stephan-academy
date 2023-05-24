from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from ContentPages.ClassDashboardPage import DashboardPage
from ContentPages.ClassLearningPage import LearningPage
from ContentPages.ClassExercisePage import ExercisePage
from ContentPages.ClassCategoryPage import CategoryPage
from ContentPages.ClassAddTextbookPage import AddTextbookPage
from ClassDBInterface import DBInterface


class MainWindow(QMainWindow):
    # Pages
    learning_page = None
    progress_dashboard_page = None


    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Resources/ui_main.ui")
        self.initUI()
        self.ui.show()



    def initUI(self):
        self.db_interface = DBInterface()
        self.progress_dashboard_page = DashboardPage(self.ui,)
        self.learning_page = LearningPage(self.ui,)
        self.exercise_page = ExercisePage(self.ui)
        self.category_page = CategoryPage(self.ui)
        self.add_textbook_page = AddTextbookPage(self.ui)
        self.learning_page.objectReferences(self.db_interface, self.exercise_page, self.category_page, self.add_textbook_page)
        self.exercise_page.objectReferences(self.db_interface, self.learning_page)
        self.category_page.objectReferences(self.db_interface, self.learning_page)
        self.add_textbook_page.objectReferences(self.db_interface, self.learning_page)
        self.connectButtons()
        self.category_page.showPage()







    def connectButtons(self):
        # Switch pages
        self.ui.button_dashboard.clicked.connect(lambda: self.switchToPage(self.progress_dashboard_page.page_number))
        self.ui.button_learn.clicked.connect(lambda: self.switchToPage(self.category_page.page_number))


    def switchToPage(self, pageNumber):
        self.ui.content_pages.setCurrentIndex(pageNumber)

