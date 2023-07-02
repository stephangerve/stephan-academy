from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from ContentPages.ClassDashboardPage import DashboardPage
from ContentPages.ClassLearningPage import LearningPage
from ContentPages.ClassExercisePage import ExercisePage
from ContentPages.ClassCategoryPage import CategoryPage
from ContentPages.ClassAddTextbookPage import AddTextbookPage
from ContentPages.ClassAddExercisesPage import AddExercisesPage
from ContentPages.ClassAddToStudyListPage import AddToStudyListPage
from ContentPages.ClassFlashcardsPage import FlashcardsPage
from ContentPages.ClassEditFlashcardsPage import EditFlashcardsPage
from ContentPages.ClassStudyFlashcardsPage import StudyFlashcardsPage
from ContentPages.ClassStudyListPage import StudyListPage
from ClassDBInterface import DBInterface
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
import ElementStyles

class MainWindow(QMainWindow):
    # Pages
    learning_page = None
    progress_dashboard_page = None


    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Resources/ui_main.ui", self)
        self.initUI()
        self.ui.show()



    def initUI(self):
        self.db_interface = DBInterface()
        self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
        self.categories = self.db_interface.fetchEntries("Categories", [])
        self.dashboard_page = DashboardPage(self.ui)
        self.learning_page = LearningPage(self.ui)
        self.exercise_page = ExercisePage(self.ui)
        self.category_page = CategoryPage(self.ui)
        self.add_textbook_page = AddTextbookPage(self.ui)
        self.add_exercises_page = AddExercisesPage(self.ui)
        self.add_to_study_list_page = AddToStudyListPage(self.ui)
        self.study_list_page = StudyListPage(self.ui)
        self.flashcards_page = FlashcardsPage(self.ui)
        self.edit_flashcards_page = EditFlashcardsPage(self.ui)
        self.study_flashcards_page = StudyFlashcardsPage(self.ui)


        self.learning_page.objectReferences(self.db_interface, self.exercise_page, self.category_page, self.add_textbook_page, self.add_exercises_page, self.add_to_study_list_page, self.study_lists)
        self.exercise_page.objectReferences(self.db_interface, self.learning_page, self.add_to_study_list_page, self.study_list_page)
        self.category_page.objectReferences(self.db_interface, self.learning_page, self.categories)
        self.add_textbook_page.objectReferences(self.db_interface, self.learning_page, self.categories)
        self.add_exercises_page.objectReferences(self.db_interface, self.learning_page)
        self.add_to_study_list_page.objectReferences(self.db_interface, self.learning_page, self.exercise_page, self.study_lists)
        self.study_list_page.objectReferences(self.db_interface, self.exercise_page, self.study_lists)
        self.flashcards_page.objectReferences(self.db_interface, self.edit_flashcards_page, self.study_flashcards_page, self.categories)
        self.edit_flashcards_page.objectReferences(self.db_interface, self.flashcards_page, self.study_flashcards_page, self.categories)
        self.study_flashcards_page.objectReferences(self.edit_flashcards_page, self.flashcards_page)
        self.connectButtons()
        self.category_page.showPage()




    def connectButtons(self):
        # Switch pages
        #self.ui.button_dashboard.clicked.connect(lambda: self.progress_dashboard_page.showPage())
        self.ui.button_dashboard.clicked.connect(lambda: self.dashboard_page.showPage())
        self.ui.button_learn.clicked.connect(lambda: self.category_page.showPage())
        self.ui.button_studylist.clicked.connect(lambda: self.study_list_page.showPage())
        self.ui.button_flashcards.clicked.connect(lambda: self.flashcards_page.showPage())

        ElementStyles.hoverEffectSideBar(self.ui.button_dashboard_frame)
        self.ui.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.hoverEffectSideBar(self.ui.button_learn_frame)
        self.ui.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.hoverEffectSideBar(self.ui.button_studylist_frame)
        self.ui.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.hoverEffectSideBar(self.ui.button_flashcards_frame)
        self.ui.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)

    def mousePressEvent(self, event):
        if self.ui.content_pages.currentIndex() == self.add_exercises_page.page_number:
            if event.button() == Qt.LeftButton:
                if self.ui.extracted_images_gridlayout.count() > 0:
                    childWidget = self.childAt(event.pos())
                    while type(childWidget) != QWidget:
                        childWidget = childWidget.parent()
                    if len(childWidget.children()) > 0:
                        try:
                            if type(childWidget.children()[2]) == QLabel:
                                if "Exercise" in childWidget.children()[2].text() or "Solution" in childWidget.children()[2].text():
                                    self.add_exercises_page.extractedImageEntryClicked(childWidget)
                        except:
                            pass
        elif self.ui.content_pages.currentIndex() == self.edit_flashcards_page.page_number:
            if event.button() == Qt.LeftButton:
                if self.ui.imported_flashcards_gridlayout.count() > 0:
                    childWidget = self.childAt(event.pos())
                    while type(childWidget) != QWidget:
                        childWidget = childWidget.parent()
                    if len(childWidget.children()) > 0:
                        try:
                            if type(childWidget.children()[2]) == QLabel:
                                if "Flashcard" in childWidget.children()[2].text():
                                    self.edit_flashcards_page.importedFlashcardEntryClicked(childWidget)
                        except:
                            pass