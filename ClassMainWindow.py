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
from ContentPages.ClassTestPage import TestPage
from ClassDBInterface import DBInterface
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QListWidget
import ElementStyles

class MainWindow(QMainWindow):
    # Pages
    learning_page = None
    progress_dashboard_page = None


    def __init__(self):
        super().__init__()
        #self.ui = uic.loadUi("Resources/ui_main.ui", self)
        self.ui = uic.loadUi("Resources/ui_main.ui", self)
        self.initUI()
        #self.test_page = TestPage()
        #self.ui.content_pages.addWidget(self.test_page)
        #self.ui.content_pages.setCurrentIndex(11)
        self.ui.show()


    def initUI(self):
        #self.setMouseTracking(True)
        self.db_interface = DBInterface()
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


        self.learning_page.objectReferences(self.db_interface, self.exercise_page, self.category_page, self.add_textbook_page, self.add_exercises_page, self.add_to_study_list_page)
        self.exercise_page.objectReferences(self.db_interface, self.learning_page, self.add_to_study_list_page, self.study_list_page)
        self.category_page.objectReferences(self.db_interface, self.learning_page, self.categories)
        self.add_textbook_page.objectReferences(self.db_interface, self.learning_page, self.categories)
        self.add_exercises_page.objectReferences(self.db_interface, self.learning_page)
        self.add_to_study_list_page.objectReferences(self.db_interface, self.learning_page, self.exercise_page)
        self.study_list_page.objectReferences(self.db_interface, self.exercise_page)
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
        elif self.ui.content_pages.currentIndex() == self.study_list_page.page_number:
            if event.button() == Qt.LeftButton:
                sl_coll_names = [sl["CollectionName"] for sl in self.study_list_page.study_list_collections]
                childWidget = self.childAt(event.pos())
                while True:
                    #print(childWidget)
                    if childWidget is not None:
                        if len(childWidget.children()) == 5:
                            if type(childWidget.children()[2]) == QLabel:
                                if childWidget.children()[2].text() in sl_coll_names:
                                    self.study_list_page.slCollectionClicked(childWidget.children()[2].text(), childWidget.parent())
                        childWidget = childWidget.parent()
                    else:
                        break



    # #Call setMouseTracking(True) for desired widget
    # def mouseMoveEvent(self, event):
    #     if self.ui.content_pages.currentIndex() == self.study_list_page.page_number:
    #         self.setMouseTracking(True)
    #         study_list_names = [sl["StudyListName"] for sl in self.study_list_page.study_lists]
    #         #if event.type() == QEvent.Enter:
    #         childWidget = self.childAt(event.pos())
    #         #childWidget = MainWindow
    #         if self.study_list_page.study_lists is not None:
    #             while True:
    #                 print(childWidget)
    #                 if childWidget is not None:
    #                     if len(childWidget.children()) > 6:
    #                         if type(childWidget.children()[5]) == QLabel:
    #                             if childWidget.children()[5].text() in study_list_names:
    #                                 pass
    #                                 pass
    #                             break
    #                     childWidget = childWidget.parent()
    #                 else:
    #                     break
    #
    # def setMouseTracking(self, flag):
    #     def recursive_set(parent):
    #         for child in parent.findChildren(QObject):
    #             try:
    #                 child.setMouseTracking(flag)
    #             except:
    #                 pass
    #             recursive_set(child)
    #
    #     QWidget.setMouseTracking(self, flag)
    #     recursive_set(self)




