import ElementStyles
from ContentPages.ClassPage import Page
from UIElements import ListElement
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QLabel, QHeaderView, QCheckBox, QPushButton
from PyQt5.QtGui import QFont, QCursor, QPixmap, QImage
from PyQt5.QtCore import Qt
import Config
import random
import string
from datetime import date
from operator import itemgetter
import matplotlib.pyplot as plt
import io
import numpy as np


class FlashcardsPage(Page):

    def __init__(self, ui):
        Page.__init__(self, Config.FlashcardsPage_page_number)
        self.ui = ui
        self.collection_list_element = ListElement(self.ui.collection_listwidget)
        self.flashcard_sets_list_element = ListElement(self.ui.flashcard_sets_listwidget)
        self.collection_txtbks = []
        ElementStyles.regularShadow(self.ui.textbook_info_frame_left_3)
        ElementStyles.regularShadow(self.ui.ex_stats_info_3)
        ElementStyles.regularShadow(self.ui.start_fc_button_frame)
        ElementStyles.regularShadow(self.ui.edit_flashcard_frame)
        ElementStyles.regularShadow(self.ui.generate_empty_set_button_frame)
        ElementStyles.lightShadow(self.ui.start_fc_button)
        ElementStyles.lightShadow(self.ui.mode_frame_3)
        ElementStyles.lightShadow(self.ui.grade_filter_frame_3)


    def objectReferences(self, db_interface, edit_flashcards_page, study_flashcards_page, categories):
        self.db_interface = db_interface
        self.edit_flashcards_page = edit_flashcards_page
        self.study_flashcards_page = study_flashcards_page
        self.categories = categories
        cat_list = [""]
        cat_list += [entry["Category"] for entry in self.categories]
        self.ui.collection_category_combobox.addItems(cat_list)


    def showPage(self):
        self.prev_selected_collection_widget = None
        self.prev_selected_flashcard_set = None
        self.selected_collection_txtbk = None
        try:
            self.ui.edit_flashcard_button.clicked.disconnect()
        except:
            pass
        if self.ui.collection_listwidget.count() > 0:
            self.ui.collection_listwidget.itemClicked.disconnect()
        if self.ui.flashcard_sets_listwidget.count() > 0:
            self.ui.flashcard_sets_listwidget.itemClicked.disconnect()
        self.flashcard_sets_list_element.clear()
        self.ui.start_fc_button_frame.setStyleSheet("background-color: gray")
        self.ui.start_fc_button.setStyleSheet("color: black")
        self.ui.start_fc_button.setEnabled(False)
        self.ui.button_flashcards.setChecked(True)
        self.ui.button_flashcards.setEnabled(False)
        self.ui.button_flashcards.setStyleSheet("background-color: rgb(58, 74, 97); color: white")
        self.ui.button_flashcards.setCursor(QCursor(QtCore.Qt.ArrowCursor))
        pushbuttons = [self.ui.button_dashboard, self.ui.button_studylist, self.ui.button_learn]
        for button in pushbuttons:
            if button.isChecked():
                button.setChecked(False)
                button.setEnabled(True)
                button.setStyleSheet("background-color: #2A4D87; color: white")
                button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.ui.create_collection_button.clicked.connect(lambda: self.createCollection())
        self.ui.add_set_button.clicked.connect(lambda: self.createSet())
        self.ui.collection_category_combobox.currentTextChanged.connect(lambda: self.generateTextbookComboBoxItems())
        self.updateCollectionListWidget()
        self.ui.content_pages.setCurrentIndex(self.page_number)

    def updateCollectionListWidget(self):
        self.ui.start_fc_button_frame.setStyleSheet("background-color: grey")
        self.ui.start_fc_button.setStyleSheet("color: black")
        self.ui.start_fc_button.setEnabled(False)
        try:
            self.ui.collection_listwidget.itemClicked.disconnect()
        except:
            pass
        self.collection_list = self.db_interface.fetchEntries("Flashcard Collections", [])
        txtbk_ids = [entry["TextbookID"] for entry in self.collection_txtbks]
        for entry in self.collection_list:
            if entry["TextbookID"] not in txtbk_ids:
                self.collection_txtbks.append(self.db_interface.fetchEntries("Textbook Info", [entry["TextbookID"]])[0])
        self.collection_txtbks = sorted(self.collection_txtbks, key=itemgetter('Category', 'Authors', 'Title', 'Edition'))
        self.collection_list_element.setList("Flashcard Collections", self.collection_txtbks)
        self.ui.collection_listwidget.itemClicked.connect(lambda: self.setFlashcardSetListWidget(self.ui.collection_listwidget.currentItem()))

    def setFlashcardSetListWidget(self, listwidgetitem):
        self.ui.start_fc_button_frame.setStyleSheet("background-color: grey")
        self.ui.start_fc_button.setStyleSheet("color: black")
        self.ui.start_fc_button.setEnabled(False)
        listwidgetitem_widgets = self.ui.collection_listwidget.itemWidget(listwidgetitem).children()
        self.selected_collection_txtbk = [entry for entry in self.collection_txtbks
                                          if entry["Category"] == listwidgetitem_widgets[1].text()
                                          and entry["Authors"] == listwidgetitem_widgets[2].text()
                                          and entry["Title"] == listwidgetitem_widgets[3].text()
                                          and entry["Edition"] == listwidgetitem_widgets[4].text()
                                          ][0]
        self.selected_collection = [entry for entry in self.collection_list if entry["TextbookID"] == self.selected_collection_txtbk["TextbookID"]][0]
        ElementStyles.selectedListItem(self.ui.collection_listwidget.itemWidget(listwidgetitem))
        if self.prev_selected_collection_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_collection_widget)
        self.prev_selected_collection_widget = self.ui.collection_listwidget.itemWidget(listwidgetitem)
        self.updateFlashcardSetListWidget()
        self.generateFlashcardSetComboBoxItems()

    def updateFlashcardSetListWidget(self):
        self.prev_selected_flashcard_set = None
        try:
            self.ui.flashcard_sets_listwidget.itemClicked.disconnect()
        except:
            pass
        self.selected_flashcard_sets = self.db_interface.fetchEntries("Flashcard Sets", [self.selected_collection["CollectionID"]])
        self.flashcard_sets_list_element.setList("Flashcard Sets", [[entry["ChapterNumber"], entry["SectionNumber"]] for entry in self.selected_flashcard_sets])
        self.ui.flashcard_sets_listwidget.itemClicked.connect(lambda: self.showFlashcardInfoPanel(self.ui.flashcard_sets_listwidget.currentItem()))
        pass
        pass

    def showFlashcardInfoPanel(self, listwidgetitem):
        listwidgetitem_widgets = self.ui.flashcard_sets_listwidget.itemWidget(listwidgetitem).children()
        self.selected_flashcard_set = [set for set in self.selected_flashcard_sets if set["ChapterNumber"] == listwidgetitem_widgets[1].text() and set["SectionNumber"] == listwidgetitem_widgets[2].text()][0]

        self.ui.start_fc_button_frame.setStyleSheet("background-color: rgb(0, 170, 127)")
        self.ui.start_fc_button.setStyleSheet("color: white")
        self.ui.start_fc_button.setEnabled(True)

        ElementStyles.selectedListItem(self.ui.flashcard_sets_listwidget.itemWidget(listwidgetitem))
        if self.prev_selected_flashcard_set is not None:
            ElementStyles.unselectedListItem(self.prev_selected_flashcard_set)
        self.prev_selected_flashcard_set = self.ui.flashcard_sets_listwidget.itemWidget(listwidgetitem)
        self.ui.set_chapter_info_label.setText(listwidgetitem_widgets[1].text())
        self.ui.set_section_info_label.setText(listwidgetitem_widgets[2].text())
        self.ui.start_fc_button.clicked.connect(lambda: self.study_flashcards_page.showPage())
        self.ui.edit_flashcard_button.clicked.connect(lambda: self.edit_flashcards_page.showPage(self.selected_collection, self.selected_flashcard_set, self.selected_collection_txtbk))



    def generateTextbookComboBoxItems(self):
        txtbks = self.db_interface.fetchEntries("Textbooks", [self.ui.collection_category_combobox.currentText()])
        txtbks_items = [" - ".join([txtbk["Authors"], txtbk["Title"], txtbk["Edition"]]) for txtbk in txtbks]
        self.txtbk_dict = dict(zip(txtbks_items, [txtbk["TextbookID"] for txtbk in txtbks]))
        txtbks_items = [""] + txtbks_items
        self.ui.collection_txtbk_combobox.addItems(txtbks_items)

    def generateFlashcardSetComboBoxItems(self):
        sections = self.db_interface.fetchEntries("Sections", [self.selected_collection["TextbookID"]])
        section_items = [" - ".join([section["ChapterNumber"], section["SectionNumber"]]) for section in sections]
        section_items = [""] + section_items
        self.ui.flashcard_set_combobox.addItems(section_items)

    def createCollection(self):
        if self.ui.collection_category_combobox.currentText() != "" and self.ui.collection_txtbk_combobox.currentText() != "":
            add_row = []
            add_row.append(self.generateCode())
            add_row.append(self.txtbk_dict[self.ui.collection_txtbk_combobox.currentText()])
            add_row.append(date.today().strftime("%m/%d/%Y"))
            self.db_interface.insertEntry("Flashcard Collection", add_row)
        self.updateCollectionListWidget()

    def createSet(self):
        if self.ui.flashcard_set_combobox.currentText() != "":
            chap_num, sect_num = self.ui.flashcard_set_combobox.currentText().split(" - ")
            add_row = []
            add_row.append(self.selected_collection["CollectionID"])
            add_row.append(self.generateCode())
            add_row.append(chap_num)
            add_row.append(sect_num)
            add_row.append(date.today().strftime("%m/%d/%Y"))
            self.db_interface.insertEntry("Flashcard Set", add_row)
        self.updateFlashcardSetListWidget()



    def generateCode(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
