from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from ContentPages.ClassDashboardPage import DashboardPage
from ContentPages.ClassLearningPage import LearningPage
from ContentPages.ClassPracticePage import PracticePage
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
from PyQt5.QtGui import QCursor
import ElementStyles
import Config

class MainWindow(QMainWindow):
    # Pages
    learning_page = None
    progress_dashboard_page = None


    def __init__(self):
        super().__init__()
        uic.loadUi("Resources/UI/main_window.ui", self)
        self.initUI()
        #self.test_page = TestPage()
        #self.content_pages.addWidget(self.test_page)
        #self.content_pages.setCurrentIndex(11)
        self.show()


    def initUI(self):
        self.db_interface = DBInterface()
        self.categories = self.db_interface.fetchEntries("Categories", [])



        self.dashboard_page = DashboardPage(self.content_pages)
        self.categories_page = CategoryPage(self.content_pages)
        self.learning_page = LearningPage(self.content_pages)
        self.practice_page = PracticePage(self.content_pages)
        self.add_textbook_page = AddTextbookPage(self.content_pages)
        self.add_exercises_page = AddExercisesPage(self.content_pages)
        self.add_to_study_list_page = AddToStudyListPage(self.content_pages)
        self.study_list_page = StudyListPage(self.content_pages)
        self.flashcards_page = FlashcardsPage(self.content_pages)
        self.edit_flashcards_page = EditFlashcardsPage(self.content_pages)
        self.study_flashcards_page = StudyFlashcardsPage(self.content_pages)

        self.content_pages.addWidget(self.dashboard_page)
        self.content_pages.addWidget(self.categories_page)
        self.content_pages.addWidget(self.learning_page)
        self.content_pages.addWidget(self.practice_page)
        self.content_pages.addWidget(self.add_textbook_page)
        self.content_pages.addWidget(self.add_exercises_page)
        self.content_pages.addWidget(self.add_to_study_list_page)
        self.content_pages.addWidget(self.study_list_page)
        self.content_pages.addWidget(self.flashcards_page)
        self.content_pages.addWidget(self.edit_flashcards_page)
        self.content_pages.addWidget(self.study_flashcards_page)


        self.learning_page.objectReferences(self.db_interface, self.practice_page, self.categories_page, self.add_textbook_page, self.add_exercises_page, self.add_to_study_list_page)
        self.practice_page.objectReferences(self.db_interface, self.learning_page, self.add_to_study_list_page, self.study_list_page)
        self.categories_page.objectReferences(self.db_interface, self.learning_page, self.categories)
        self.add_textbook_page.objectReferences(self.db_interface, self.learning_page, self.categories)
        self.add_exercises_page.objectReferences(self.db_interface, self.learning_page)
        self.add_to_study_list_page.objectReferences(self.db_interface, self.learning_page, self.practice_page)
        self.study_list_page.objectReferences(self.db_interface, self.practice_page)
        self.flashcards_page.objectReferences(self.db_interface, self.edit_flashcards_page, self.study_flashcards_page, self.categories)
        self.edit_flashcards_page.objectReferences(self.db_interface, self.flashcards_page, self.study_flashcards_page, self.categories)
        self.study_flashcards_page.objectReferences(self.db_interface, self.edit_flashcards_page, self.flashcards_page)
        self.connectSideBarButtons()
        self.sideBarButtonClicked(self.button_learn, self.categories_page)


    def connectSideBarButtons(self):
        # Switch pages
        #self.button_dashboard.clicked.connect(lambda: self.progress_dashboard_page.showPage())
        self.button_dashboard.clicked.connect(lambda: self.sideBarButtonClicked(self.button_dashboard, self.dashboard_page))
        self.button_learn.clicked.connect(lambda: self.sideBarButtonClicked(self.button_learn, self.categories_page))
        self.button_studylist.clicked.connect(lambda: self.sideBarButtonClicked(self.button_studylist, self.study_list_page))
        self.button_flashcards.clicked.connect(lambda: self.sideBarButtonClicked(self.button_flashcards, self.flashcards_page))
        self.side_bar_buttons = [self.button_dashboard, self.button_learn, self.button_studylist, self.button_flashcards]

        ElementStyles.hoverEffectSideBar(self.button_dashboard_frame)
        self.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.hoverEffectSideBar(self.button_learn_frame)
        self.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.hoverEffectSideBar(self.button_studylist_frame)
        self.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.hoverEffectSideBar(self.button_flashcards_frame)
        self.button_dashboard.setWindowFlags(Qt.FramelessWindowHint)
        self.button_dashboard.setAttribute(Qt.WA_TranslucentBackground)



    def sideBarButtonClicked(self, clicked_button, next_page):
        clicked_button.setChecked(True)
        clicked_button.setEnabled(False)
        clicked_button.setStyleSheet("background-color: rgb(58, 74, 97); color: white")
        clicked_button.setCursor(QCursor(QtCore.Qt.ArrowCursor))
        for button in self.side_bar_buttons:
            if button != clicked_button:
                if button.isChecked():
                    button.setChecked(False)
                    button.setEnabled(True)
                    button.setStyleSheet("background-color: #2A4D87; color: white")
                    button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        next_page.showPage()

        # #Call setMouseTracking(True) for desired widget
        # def mouseMoveEvent(self, event):
        #     if self.content_pages.currentIndex() == self.study_list_page.page_number:
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




