from PyQt5 import uic
import ElementStyles
from ContentPages.ClassPage import Page
from CustomWidgets.ClassCustomListWidget import CustomListWidget
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QLabel, QHeaderView, QCheckBox, QPushButton, QWidget
from PyQt5.QtGui import QFont, QCursor, QPixmap, QImage
from PyQt5.QtCore import Qt
import Config
import random
import string
from datetime import date
from operator import itemgetter
import matplotlib.pyplot as plt
import io, os
import numpy as np


class FlashcardsPage(Page):

    def __init__(self, content_pages):
        Page.__init__(self, Config.FlashcardsPage_page_number)
        uic.loadUi('Resources/UI/flashcards_page.ui', self)
        self.content_pages = content_pages
        self.collection_txtbks = []
        ElementStyles.regularShadow(self.textbook_info_frame_left_3)
        ElementStyles.regularShadow(self.ex_stats_info_3)
        ElementStyles.regularShadow(self.start_fc_button_frame)
        ElementStyles.regularShadow(self.edit_flashcard_frame)
        ElementStyles.regularShadow(self.generate_empty_set_button_frame)
        ElementStyles.lightShadow(self.start_fc_button)
        ElementStyles.lightShadow(self.mode_frame_3)
        ElementStyles.lightShadow(self.grade_filter_frame_3)



    def objectReferences(self, db_interface, edit_flashcards_page, study_flashcards_page, categories):
        self.db_interface = db_interface
        self.edit_flashcards_page = edit_flashcards_page
        self.study_flashcards_page = study_flashcards_page
        self.categories = categories
        cat_list = [""]
        cat_list += [entry["Category"] for entry in self.categories]
        self.collection_category_combobox.addItems(cat_list)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.imported_flashcards_gridlayout.count() > 0:
                childWidget = self.childAt(event.pos())
                while type(childWidget) != QWidget:
                    childWidget = childWidget.parent()
                if len(childWidget.children()) > 0:
                    try:
                        if type(childWidget.children()[2]) == QLabel:
                            if "Flashcard" in childWidget.children()[2].text():
                                self.importedFlashcardEntryClicked(childWidget)
                    except:
                        pass


    def showPage(self):
        self.prev_selected_textbook_widget = None
        self.prev_selected_category_item_widget = None
        self.prev_selected_flashcard_set = None
        self.selected_collection_txtbk = None
        try:
            self.edit_flashcard_button.clicked.disconnect()
        except:
            pass
        if self.collection_category_listwidget.count() > 0:
            self.collection_category_listwidget.itemClicked.disconnect()
        if self.collection_textbook_listwidget.count() > 0:
            self.collection_textbook_listwidget.itemClicked.disconnect()
        if self.flashcard_sets_listwidget.count() > 0:
            self.flashcard_sets_listwidget.itemClicked.disconnect()
        self.flashcard_sets_listwidget.clear()
        self.start_fc_button_frame.setStyleSheet("background-color: gray")
        self.start_fc_button.setStyleSheet("color: black")
        self.start_fc_button.setEnabled(False)
        self.create_collection_button.clicked.connect(lambda: self.createCollection())
        self.add_set_button.clicked.connect(lambda: self.createSet())
        self.collection_category_combobox.currentTextChanged.connect(lambda: self.generateTextbookComboBoxItems())

        self.collection_list = self.db_interface.fetchEntries("Flashcard Collections", [])
        txtbk_ids = [entry["TextbookID"] for entry in self.collection_txtbks]
        for entry in self.collection_list:
            if entry["TextbookID"] not in txtbk_ids:
                self.collection_txtbks.append(self.db_interface.fetchEntries("Textbook Info", [entry["TextbookID"]])[0])
        self.collection_txtbks = sorted(self.collection_txtbks, key=itemgetter('Category', 'Authors', 'Title', 'Edition'))
        self.categories = sorted(list(set([entry["Category"] for entry in self.collection_txtbks])))

        self.setCategoriesListWidget()
        self.content_pages.setCurrentIndex(self.page_number)

    def setCategoriesListWidget(self):
        self.prev_selected_category_item_widget = None
        self.prev_selected_textbook_widget = None
        self.prev_selected_flashcard_set = None

        self.collection_category_listwidget.clear()
        self.collection_textbook_listwidget.clear()
        self.flashcard_sets_listwidget.clear()

        self.start_fc_button_frame.setStyleSheet("background-color: grey")
        self.start_fc_button.setStyleSheet("color: black")
        self.start_fc_button.setEnabled(False)
        try:
            self.collection_category_listwidget.itemClicked.disconnect()
            self.collection_textbook_listwidget.itemClicked.disconnect()
        except:
            pass

        self.collection_category_listwidget.setList("Flashcard Categories", self.categories)
        self.collection_category_listwidget.itemClicked.connect(lambda: self.categoryLWClicked(self.collection_category_listwidget.currentItem()))


    def categoryLWClicked(self, listwidgetitem): #categories listwidget clicked
        self.prev_selected_textbook_widget = None
        self.prev_selected_flashcard_set = None

        self.collection_textbook_listwidget.clear()
        self.flashcard_sets_listwidget.clear()


        if self.prev_selected_category_item_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_category_item_widget)
        self.prev_selected_category_item_widget = self.collection_category_listwidget.itemWidget(listwidgetitem)
        ElementStyles.selectedListItem(self.prev_selected_category_item_widget)
        self.selected_category = self.prev_selected_category_item_widget.children()[1].text()

        self.selected_category_textbooks = [entry for entry in self.collection_txtbks if entry["Category"] == self.selected_category]
        self.collection_textbook_listwidget.setList("Flashcard Textbooks", self.selected_category_textbooks)
        self.collection_textbook_listwidget.itemClicked.connect(lambda: self.textbookLWClicked(self.collection_textbook_listwidget.currentItem()))
        self.flashcards_images_dir = os.path.join(Config.FLASHCARDS_DIR, self.selected_category)

    def textbookLWClicked(self, listwidgetitem):
        self.prev_selected_flashcard_set = None

        self.flashcard_sets_listwidget.clear()

        self.start_fc_button_frame.setStyleSheet("background-color: grey")
        self.start_fc_button.setStyleSheet("color: black")
        self.start_fc_button.setEnabled(False)
        listwidgetitem_widgets = self.collection_textbook_listwidget.itemWidget(listwidgetitem).children()
        self.selected_collection_txtbk = [entry for entry in self.collection_txtbks
                                          if entry["Authors"] == listwidgetitem_widgets[1].text()
                                          and entry["Title"] == listwidgetitem_widgets[2].text()
                                          and entry["Edition"] == listwidgetitem_widgets[3].text()
                                          ][0]
        self.selected_collection = [entry for entry in self.collection_list if entry["TextbookID"] == self.selected_collection_txtbk["TextbookID"]][0]
        if self.prev_selected_textbook_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_textbook_widget)
        self.prev_selected_textbook_widget = self.collection_textbook_listwidget.itemWidget(listwidgetitem)
        ElementStyles.selectedListItem(self.prev_selected_textbook_widget)
        self.updateFlashcardSetListWidget()
        self.generateFlashcardSetComboBoxItems()
        self.flashcards_images_dir = os.path.join(self.flashcards_images_dir, " - ".join([self.selected_collection_txtbk["Authors"], self.selected_collection_txtbk["Title"]]))
        if self.selected_collection_txtbk["Title"] != "1st":
            self.flashcards_images_dir = self.flashcards_images_dir + " - " + self.selected_collection_txtbk["Edition"]
        self.flashcards_images_dir = os.path.join(self.flashcards_images_dir, "Flashcards Images")

    def updateFlashcardSetListWidget(self):
        self.prev_selected_flashcard_set = None
        try:
            self.flashcard_sets_listwidget.itemClicked.disconnect()
        except:
            pass
        self.selected_flashcard_sets = self.db_interface.fetchEntries("Flashcard Sets", [self.selected_collection["CollectionID"]])
        self.flashcard_sets_listwidget.setList("Flashcard Sets", [[entry["ChapterNumber"], entry["SectionNumber"]] for entry in self.selected_flashcard_sets])
        self.flashcard_sets_listwidget.itemClicked.connect(lambda: self.showFlashcardInfoPanel(self.flashcard_sets_listwidget.currentItem()))
        pass
        pass

    def showFlashcardInfoPanel(self, listwidgetitem):
        listwidgetitem_widgets = self.flashcard_sets_listwidget.itemWidget(listwidgetitem).children()
        self.selected_flashcard_set = [set for set in self.selected_flashcard_sets if set["ChapterNumber"] == listwidgetitem_widgets[3].text() and set["SectionNumber"] == listwidgetitem_widgets[4].text()][0]
        self.selected_set_flashcards = self.db_interface.fetchEntries("Flashcards", [self.selected_flashcard_set["CollectionID"], self.selected_flashcard_set["SetID"]])
        self.flashcards_images_dir = os.path.join(self.flashcards_images_dir, ".".join([self.selected_flashcard_set["ChapterNumber"].zfill(2), self.selected_flashcard_set["SectionNumber"].zfill(2)]))
        self.start_fc_button_frame.setStyleSheet("background-color: rgb(0, 170, 127)")
        self.start_fc_button.setStyleSheet("color: white")
        self.start_fc_button.setEnabled(True)

        ElementStyles.selectedListItem(self.flashcard_sets_listwidget.itemWidget(listwidgetitem))
        if self.prev_selected_flashcard_set is not None:
            ElementStyles.unselectedListItem(self.prev_selected_flashcard_set)
        self.prev_selected_flashcard_set = self.flashcard_sets_listwidget.itemWidget(listwidgetitem)
        self.set_chapter_info_label.setText(listwidgetitem_widgets[3].text())
        self.set_section_info_label.setText(listwidgetitem_widgets[4].text())
        self.start_fc_button.clicked.connect(lambda state, flashcards=self.selected_set_flashcards, flashcards_images_dir=self.flashcards_images_dir: self.study_flashcards_page.showPage(flashcards, flashcards_images_dir))
        self.edit_flashcard_button.clicked.connect(lambda: self.edit_flashcards_page.showPage(self.selected_collection, self.selected_flashcard_set, self.selected_collection_txtbk))



    def generateTextbookComboBoxItems(self):
        txtbks = self.db_interface.fetchEntries("Textbooks", [self.collection_category_combobox.currentText()])
        txtbks_items = [" - ".join([txtbk["Authors"], txtbk["Title"], txtbk["Edition"]]) for txtbk in txtbks]
        self.txtbk_dict = dict(zip(txtbks_items, [txtbk["TextbookID"] for txtbk in txtbks]))
        txtbks_items = [""] + txtbks_items
        self.collection_txtbk_combobox.addItems(txtbks_items)

    def generateFlashcardSetComboBoxItems(self):
        sections = self.db_interface.fetchEntries("Sections", [self.selected_collection["TextbookID"]])
        section_items = [" - ".join([section["ChapterNumber"], section["SectionNumber"]]) for section in sections]
        section_items = [""] + section_items
        self.flashcard_set_combobox.addItems(section_items)

    def createCollection(self):
        if self.collection_category_combobox.currentText() != "" and self.collection_txtbk_combobox.currentText() != "":
            add_row = []
            add_row.append(self.generateCode())
            add_row.append(self.txtbk_dict[self.collection_txtbk_combobox.currentText()])
            add_row.append(date.today().strftime("%m/%d/%Y"))
            add_row = tuple(add_row)
            self.db_interface.insertEntry("Flashcard Collection", add_row)
        self.updateCollectionListWidget()

    def createSet(self):
        if self.flashcard_set_combobox.currentText() != "":
            chap_num, sect_num = self.flashcard_set_combobox.currentText().split(" - ")
            add_row = []
            add_row.append(self.selected_collection["CollectionID"])
            add_row.append(self.generateCode())
            add_row.append(chap_num)
            add_row.append(sect_num)
            add_row.append(date.today().strftime("%m/%d/%Y"))
            add_row = tuple(add_row)
            self.db_interface.insertEntry("Flashcard Set", add_row)
        self.updateFlashcardSetListWidget()



    def generateCode(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
