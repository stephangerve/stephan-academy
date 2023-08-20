import ElementStyles
from ContentPages.ClassPage import Page
from CustomWidgets.ClassListWidget import ListWidget
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QFrame, QPushButton, QHBoxLayout, QFileDialog, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont, QCursor, QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import Config
import random
import string
from datetime import date
import matplotlib.pyplot as plt
import io
import numpy as np
import os
import docx2pdf
import pdf2image
import docx
import shutil
from datetime import date



class EditFlashcardsPage(Page):

    def __init__(self, ui):
        Page.__init__(self, Config.EditFlashcardsPage_page_number)
        self.ui = ui
        self.flashcards_in_grid = []
        self.imported_flashcards_timer = QTimer()
        self.import_button_frame = None
        self.MAX_COLS = 4
        self.prev_selected_imported_flashcard_widget = None
        self.prev_selected_set_flashcard_widget = None
        self.set_flashcard_list_elem = ListWidget(self.ui.set_flashcards_listwidget)
        ElementStyles.regularShadow(self.ui.update_card_frame)
        ElementStyles.regularShadow(self.ui.delete_card_frame)

    def objectReferences(self, db_interface, flashcards_page, study_flashcards_page, selected_collection_txtbk):
        self.db_interface = db_interface
        self.flashcards_page = flashcards_page
        self.study_flashcards_page = study_flashcards_page
        self.selected_collection_txtbk = selected_collection_txtbk

    def showPage(self, selected_collection, selected_flashcard_set, selected_collection_txtbk):
        self.selected_collection = selected_collection
        self.selected_flashcard_set = selected_flashcard_set
        self.selected_collection_txtbk = selected_collection_txtbk
        self.ui.content_pages.setCurrentIndex(self.page_number)
        self.ui.exit_edit_ex_page_button.clicked.connect(lambda: self.exitPage())
        if self.selected_collection_txtbk["Edition"] == "1st":
            txtbk_dirname = " - ".join([self.selected_collection_txtbk["Authors"], self.selected_collection_txtbk["Title"]])
        else:
            txtbk_dirname = " - ".join([self.selected_collection_txtbk["Authors"], self.selected_collection_txtbk["Title"], self.selected_collection_txtbk["Edition"]])
        if self.selected_flashcard_set["ChapterNumber"].isdigit():
            set_dirname = self.selected_flashcard_set["ChapterNumber"].zfill(2)
        else:
            set_dirname = self.selected_flashcard_set["ChapterNumber"]
        if self.selected_flashcard_set["SectionNumber"].isdigit():
            set_dirname = ".".join([set_dirname, self.selected_flashcard_set["SectionNumber"].zfill(2)])
        else:
            set_dirname = ".".join([set_dirname, self.selected_flashcard_set["SectionNumber"]])
        self.flashcard_word_files_dir = os.path.join(Config.FLASHCARDS_DIR, self.selected_collection_txtbk["Category"], txtbk_dirname, "Flashcards Word Files", set_dirname)
        self.flashcard_set_dir = os.path.join(Config.FLASHCARDS_DIR, self.selected_collection_txtbk["Category"], txtbk_dirname, "Flashcards Images", set_dirname)
        os.makedirs(self.flashcard_word_files_dir, exist_ok=True)
        os.makedirs(self.flashcard_set_dir, exist_ok=True)
        self.imported_flashcards_timer.start(1000)
        self.imported_flashcards_timer.timeout.connect(lambda: self.updateImportedFlashcardsGrid())
        self.last_grid_row_idx = 0
        self.grid_col_start_idx = 0
        if self.prev_selected_imported_flashcard_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_imported_flashcard_widget)
        self.prev_selected_imported_flashcard_widget = None
        if self.prev_selected_set_flashcard_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_set_flashcard_widget)
        self.prev_selected_set_flashcard_widget = None
        self.ui.flashcard_front_png_label.clear()
        self.ui.flashcard_back_png_label.clear()
        self.ui.add_fc_to_set_button.clicked.connect(lambda: self.addFlashcardsToSet())
        try:
            self.ui.set_flashcards_listwidget.itemClicked.disconnect()
        except:
            pass
        self.updateSetFlashcardsListWidget()




    def exitPage(self):
        self.ui.content_pages.setCurrentIndex(self.flashcards_page.page_number)
        return

    def setFlashcardEntryClicked(self, listwidgetitem):
        listwidgetitem_widgets = self.ui.set_flashcards_listwidget.itemWidget(listwidgetitem).children()

        filename_front = os.path.join(self.flashcard_set_dir, listwidgetitem_widgets[1].text().split(" ")[-1] + " - flashcard _front.png")
        qpixmap_front = QPixmap(filename_front)
        if qpixmap_front.size().width() > self.ui.png_label.size().width():
            qpixmap_front = qpixmap_front.scaled(self.ui.png_label.size().width(), qpixmap_front.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui.flashcard_front_png_label.setPixmap(qpixmap_front)
        self.ui.flashcard_front_png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.flashcard_front_png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.ui.flashcard_front_png_label)

        filename_back = os.path.join(self.flashcard_set_dir, listwidgetitem_widgets[1].text().split(" ")[-1] + " - flashcard back.png")
        qpixmap_back = QPixmap(filename_back)
        if qpixmap_back.size().width() > self.ui.png_label.size().width():
            qpixmap_back = qpixmap_back.scaled(self.ui.png_label.size().width(), qpixmap_back.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui.flashcard_back_png_label.setPixmap(qpixmap_back)
        self.ui.flashcard_back_png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.flashcard_back_png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.ui.flashcard_back_png_label)


        ElementStyles.selectedListItem(self.ui.set_flashcards_listwidget.itemWidget(listwidgetitem))
        if self.prev_selected_set_flashcard_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_set_flashcard_widget)
        self.prev_selected_set_flashcard_widget = self.ui.set_flashcards_listwidget.itemWidget(listwidgetitem)

        if self.prev_selected_imported_flashcard_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_imported_flashcard_widget)
        self.prev_selected_imported_flashcard_widget = None



    def updateSetFlashcardsListWidget(self):
        self.set_flashcards = self.db_interface.fetchEntries("Flashcards", [self.selected_collection["CollectionID"], self.selected_flashcard_set["SetID"]])
        self.set_flashcard_list_elem.setList("Set Flashcards", self.set_flashcards)
        self.ui.set_flashcards_listwidget.itemClicked.connect(lambda: self.setFlashcardEntryClicked(self.ui.set_flashcards_listwidget.currentItem()))




    def addFlashcardsToSet(self):
        if len(self.flashcards_in_grid) > 0:
            for fc_dict in self.flashcards_in_grid:
                filename_front = os.path.join(Config.TEMP_FC_PATH, fc_dict["Front"])
                shutil.move(filename_front, os.path.join(self.flashcard_set_dir, fc_dict["Front"]))
                filename_back = os.path.join(Config.TEMP_FC_PATH, fc_dict["Back"])
                shutil.move(filename_back, os.path.join(self.flashcard_set_dir, fc_dict["Back"]))
                today = date.today().strftime("%m/%d/%Y")
                add_row = (self.selected_collection["CollectionID"], self.selected_flashcard_set["SetID"], fc_dict["FlashcardID"], today, today, str(False), 0, None, None, None, None, None)
                self.db_interface.insertEntry("New Flashcard", add_row)
            self.updateSetFlashcardsListWidget()



    def importFlashcards(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        filepath = file_dialog.getOpenFileName(None, 'Select Folder', self.flashcard_word_files_dir)
        if filepath != ('', ''):
            self.setCursor(QCursor(QtCore.Qt.WaitCursor))
            self.clearImagesGrid()
            docx_file = list(filepath)[0]
            doc = docx.Document(docx_file)
            flashcardIDs = []
            for page in doc.sections:
                flashcardID = page.footer.paragraphs[0].text.split('\t\t')[-1]
                if flashcardID not in flashcardIDs:
                    flashcardIDs.append(flashcardID)
            temp_pdf_path = docx_file.split("\\")[-1].split(".docx")[0] + ".pdf"
            if not os.path.exists(temp_pdf_path):
                docx2pdf.convert(docx_file, temp_pdf_path)
            images = pdf2image.convert_from_path(temp_pdf_path, 400, size=(500, 300))
            idx = 0
            for i in range(len(images)):
                if (i + 1) % 2 != 0:
                    png_name = os.path.join(Config.TEMP_FC_PATH, str(flashcardIDs[idx]).zfill(3) + " - flashcard _front.png")
                else:
                    png_name = os.path.join(Config.TEMP_FC_PATH, str(flashcardIDs[idx]).zfill(3) + " - flashcard back.png")
                    idx += 1
                if not os.path.exists(os.path.join(Config.TEMP_FC_PATH, png_name)):
                    images[i].save(os.path.join(Config.TEMP_FC_PATH, png_name))
                    #print("Added: " + png_name)
            os.remove(temp_pdf_path)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

    def extractedImageWidget(self, file_dict):
        widget_width = 200
        widget_height = 80

        qpixmap_fc_front = QPixmap(os.path.join(Config.TEMP_FC_PATH, file_dict["Front"]))
        qpixmap_fc_front = qpixmap_fc_front.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        pic_front_label = QLabel()
        pic_front_label.setPixmap(qpixmap_fc_front)
        pic_front_label.setAlignment(Qt.AlignCenter)
        pic_front_label.setWindowFlags(Qt.FramelessWindowHint)
        pic_front_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.lightShadow(pic_front_label)

        qpixmap_fc_back = QPixmap(os.path.join(Config.TEMP_FC_PATH, file_dict["Back"]))
        qpixmap_fc_back = qpixmap_fc_back.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        pic_back_label = QLabel()
        pic_back_label.setPixmap(qpixmap_fc_back)
        pic_back_label.setAlignment(Qt.AlignCenter)
        pic_back_label.setWindowFlags(Qt.FramelessWindowHint)
        pic_back_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.lightShadow(pic_back_label)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(pic_front_label)
        hlayout.addWidget(pic_back_label)

        pic_front_back_frame = QFrame()
        pic_front_back_frame.setWindowFlags(Qt.FramelessWindowHint)
        pic_front_back_frame.setAttribute(Qt.WA_TranslucentBackground)
        pic_front_back_frame.setLayout(hlayout)

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(5, 5, 5, 5)
        vlayout.addWidget(pic_front_back_frame)

        fn_label = QLabel("Flashcard " + file_dict["FlashcardID"])
        fn_label.setFixedSize(widget_width, 20)
        fn_label.setAlignment(Qt.AlignCenter)
        fn_label.setWindowFlags(Qt.FramelessWindowHint)
        fn_label.setAttribute(Qt.WA_TranslucentBackground)
        vlayout.addWidget(fn_label)
        widget = QWidget()
        #widget = QPushButton()
        #widget.setFlat(True)
        widget.setWindowFlags(Qt.FramelessWindowHint)
        #widget.setAttribute(Qt.WA_TranslucentBackground)
        widget.setCursor(QCursor(Qt.PointingHandCursor))
        widget.setLayout(vlayout)
        widget.setStyleSheet("background-color: #ffffff")
        ElementStyles.hoverEffect(widget)
        widget.setFixedSize(widget_width, widget_height)
        return widget

    def updateImportedFlashcardsGrid(self):
        temp_files = os.listdir(Config.TEMP_FC_PATH)
        if len(temp_files) > 0:
            if self.import_button_frame is not None:
                self.import_button_frame = None
                self.clearImagesGrid()
            flashcard_temp_files = {}
            for file in os.listdir(Config.TEMP_FC_PATH):
                flashcard_id = file.split(" ")[0]
                if flashcard_id not in flashcard_temp_files.keys():
                    flashcard_temp_files[flashcard_id] = {"Front": None, "Back": None, "FlashcardID": flashcard_id}
                if "_front" in file:
                    flashcard_temp_files[flashcard_id]["Front"] = file
                elif "back" in file:
                    flashcard_temp_files[flashcard_id]["Back"] = file
            count = len(flashcard_temp_files.keys())
            self.ui.imported_flashcard_label.setText("Imported Cards: " + str(count))
            if (len(flashcard_temp_files) - len(self.flashcards_in_grid)) > 0:
                [self.flashcards_in_grid.append(flashcard_temp_files[id]) for id in flashcard_temp_files if flashcard_temp_files[id] not in self.flashcards_in_grid]
                if count % self.MAX_COLS == 0:
                    rows = int(count / self.MAX_COLS)
                else:
                    rows = int(count / self.MAX_COLS) + 1
                for i in range(self.last_grid_row_idx, rows):
                    self.last_grid_row_idx = i
                    if int(count / ((i + 1) * self.MAX_COLS)) > 0:
                        columns = self.MAX_COLS
                    elif i > 0:
                        columns = count % (i * self.MAX_COLS)
                    else:
                        columns = count
                    for j in range(self.grid_col_start_idx, columns):
                        index = i * self.MAX_COLS + j
                        self.grid_col_start_idx = j
                        file_dict = flashcard_temp_files[list(flashcard_temp_files.keys())[index]]
                        widget = self.extractedImageWidget(file_dict)
                        self.ui.imported_flashcards_gridlayout.addWidget(widget, i, j)
                    if self.grid_col_start_idx == self.MAX_COLS - 1:
                        self.grid_col_start_idx = 0
                self.grid_col_start_idx += 1
        elif len(temp_files) == 0:
            if self.import_button_frame is None:
                self.clearImagesGrid()
                self.ui.flashcard_front_png_label.clear()
                self.ui.flashcard_back_png_label.clear()
                self.prev_selected_imported_flashcard_widget = None
                self.import_button_frame = QFrame()
                self.import_button_frame.setFixedWidth(1100)
                self.import_button_frame.setFixedHeight(380)
                self.import_button_frame.setStyleSheet("QFrame{background-color: rgb(238, 238, 236)} QFrame::hover{background-color : lightgray}")
                import_button = QPushButton("Import Flashcards")
                #import_button.setStyleSheet("color: black; font: 12pt \"Calibri Light\"")
                import_button.setStyleSheet("color: black;")
                import_button.setFixedWidth(1100)
                import_button.setFixedHeight(380)
                import_button.setFlat(True)
                # import_button.setWindowFlags(Qt.FramelessWindowHint)
                # import_button.setAttribute(Qt.WA_TranslucentBackground)
                import_button.setCursor(QCursor(Qt.PointingHandCursor))
                import_button.clicked.connect(lambda: self.importFlashcards())
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(import_button)
                self.import_button_frame.setLayout(layout)
                self.ui.imported_flashcards_gridlayout.addWidget(self.import_button_frame, 0, 0)

    def clearImagesGrid(self):
        self.flashcards_in_grid.clear()
        for i in reversed(range(self.ui.imported_flashcards_gridlayout.count())):
            self.ui.imported_flashcards_gridlayout.itemAt(i).widget().setParent(None)

    def importedFlashcardEntryClicked(self, widget):
        filename_front = [flashcard["Front"] for flashcard in self.flashcards_in_grid if flashcard["FlashcardID"] == widget.children()[2].text().split(" ")[1]][0]
        qpixmap_front = QPixmap(os.path.join(Config.TEMP_FC_PATH, filename_front))
        if qpixmap_front.size().width() > self.ui.png_label.size().width():
            qpixmap_front = qpixmap_front.scaled(self.ui.png_label.size().width(), qpixmap_front.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui.flashcard_front_png_label.setPixmap(qpixmap_front)
        self.ui.flashcard_front_png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.flashcard_front_png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.ui.flashcard_front_png_label)

        filename_back = [flashcard["Back"] for flashcard in self.flashcards_in_grid if flashcard["FlashcardID"] == widget.children()[2].text().split(" ")[1]][0]
        qpixmap_back = QPixmap(os.path.join(Config.TEMP_FC_PATH, filename_back))
        if qpixmap_back.size().width() > self.ui.png_label.size().width():
            qpixmap_back = qpixmap_back.scaled(self.ui.png_label.size().width(), qpixmap_back.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui.flashcard_back_png_label.setPixmap(qpixmap_back)
        self.ui.flashcard_back_png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.flashcard_back_png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.ui.flashcard_back_png_label)

        ElementStyles.selectedListItem(widget)
        if self.prev_selected_imported_flashcard_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_imported_flashcard_widget)
        self.prev_selected_imported_flashcard_widget = widget

        if self.prev_selected_set_flashcard_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_set_flashcard_widget)
        self.prev_selected_set_flashcard_widget = None

