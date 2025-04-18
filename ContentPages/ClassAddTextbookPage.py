from PyQt5 import uic
import ElementStyles
from ContentPages.ClassPage import Page
from ClassDBInterface import DBInterface
from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QFileDialog, QSpinBox, QTableWidgetItem, QLineEdit, QHeaderView
from PyQt5.QtGui import QFont, QPixmap, QColor, QCursor
import io
import os
import Config
import random
import string
#from tr import tr
import inflect
import shutil
p = inflect.engine()

class AddTextbookPage(Page):
    ui = None
    exercises = None
    exercise_stats = None



    def __init__(self, content_pages):
        Page.__init__(self, Config.AddTextbookPage_page_number)
        uic.loadUi('Resources/UI/add_textbook_page.ui', self)
        self.content_pages = content_pages
        self.initUI()


    def initUI(self):
        pass

    def objectReferences(self, db_interface, learning_page, categories):
        self.db_interface = db_interface
        self.learning_page = learning_page
        self.categories = categories

    def showPage(self, cat_str):
        cat_list = [""]
        cat_list += [entry["Category"] for entry in self.categories]
        self.category_combo_box.addItems(cat_list)
        self.category_combo_box.setCurrentText(cat_str)
        self.num_sections_table.setColumnCount(1)
        self.num_sections_table.setHorizontalHeaderLabels(["Chapter Number"])
        self.console_text_edit.setReadOnly(True)
        self.tb_file_path_browse_button.clicked.connect(lambda state, line_edit=self.tb_file_path_line_edit: self.browseForFile(line_edit))
        self.sm_file_path_browse_button.clicked.connect(lambda state, line_edit=self.sm_file_path_line_edit: self.browseForFile(line_edit))
        self.sections_check_box.stateChanged.connect(lambda: self.setSectionsInTable())
        self.num_chapters_spin_box.valueChanged.connect(lambda: self.insertChaptersRowsInTable())
        self.submit_button.clicked.connect(lambda: self.submitNewTextbook())
        self.clear_button.clicked.connect(lambda: self.clearFields())
        self.exit_add_textbook_page_button.clicked.connect(lambda: self.content_pages.setCurrentIndex(self.learning_page.page_number))
        self.content_pages.setCurrentIndex(self.page_number)

    def insertChaptersRowsInTable(self):
        if self.sections_check_box.isChecked():
            self.num_sections_table.setColumnCount(3)
            self.num_sections_table.setHorizontalHeaderLabels(["Chapter Number", "Number of Sections", "Starting Section Number"])
        else:
            self.num_sections_table.setColumnCount(1)
            self.num_sections_table.setHorizontalHeaderLabels(["Chapter Number"])
        if self.num_chapters_spin_box.value() > self.num_sections_table.rowCount():
            for i in range(self.num_sections_table.rowCount(), self.num_chapters_spin_box.value()):
                self.num_sections_table.insertRow(i)
                self.num_sections_table.setCellWidget(i, 0, QLineEdit(str(i + 1)))
                if self.sections_check_box.isChecked():
                    self.num_sections_table.setCellWidget(i, 1, QSpinBox())
                    self.num_sections_table.setCellWidget(i, 2, QLineEdit("1"))
        elif self.num_chapters_spin_box.value() < self.num_sections_table.rowCount():
            for i in reversed(range(self.num_chapters_spin_box.value(), self.num_sections_table.rowCount())):
                self.num_sections_table.removeRow(i)
        self.num_sections_table.verticalHeader().setVisible(False)
        self.num_sections_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        if self.sections_check_box.isChecked():
            self.num_sections_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.num_sections_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)


    def setSectionsInTable(self):
        #self.num_sections_table.setRowCount(self.num_chapters_spin_box.value())
        self.num_sections_table.verticalHeader().setVisible(False)
        self.num_sections_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        if self.sections_check_box.isChecked():
            self.num_sections_table.setColumnCount(3)
            self.num_sections_table.setHorizontalHeaderLabels(["Chapter Number", "Number of Sections", "Starting Section Number"])
            self.num_sections_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.num_sections_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        else:
            self.num_sections_table.setColumnCount(1)
            self.num_sections_table.setHorizontalHeaderLabels(["Chapter Number"])
        for i in range(self.num_sections_table.rowCount()):
            if self.sections_check_box.isChecked():
                self.num_sections_table.setCellWidget(i, 1, QSpinBox())
                self.num_sections_table.setCellWidget(i, 2, QLineEdit("1"))



    def browseForFile(self, line_edit_box):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        filepath = file_dialog.getOpenFileName(None, 'Select Folder', Config.TXTBK_SOURCE_PATH)
        line_edit_box.setText(list(filepath)[0])

    def submitNewSections(self, textbookid, sections_list):
        for row in sections_list:
            add_row = (textbookid, row[0], row[1], None, None, str(False), str(False), None, None, None)
            if not self.db_interface.fetchBool("Section Exist", add_row):
                self.db_interface.insertEntry("Section", add_row)
                self.console_text_edit.append(">> Added section to database: " + str(add_row))
            else:
                self.console_text_edit.append(">> Row exists in database: " + str(add_row))

    def submitNewTextbook(self):
        if self.author_line_edit.text() is not None and len(self.author_line_edit.text()) != 0 and \
        self.title_line_edit.text() is not None and len(self.title_line_edit.text()) != 0:
            if not self.db_interface.fetchBool("Textbooks", [self.category_combo_box.currentText(), self.author_line_edit.text(), self.title_line_edit.text(), p.ordinal(self.edition_spin_box.value())]):
                textbookid = self.generateCode()
                sections_list = []
                for i in range(self.num_sections_table.rowCount()):
                    if self.sections_check_box.isChecked():
                        for j in range(self.num_sections_table.cellWidget(i,1).value() - 1):
                            sections_list.append([self.num_sections_table.cellWidget(i,0).text(), str(j + 1)])
                        if self.eoc_check_box.isChecked():
                            sections_list.append([self.num_sections_table.cellWidget(i,0).text(), "EOC"])
                        else:
                            sections_list.append([self.num_sections_table.cellWidget(i, 0).text(), str(self.num_sections_table.cellWidget(i,1).value())])
                    else:
                        sections_list.append([self.num_sections_table.cellWidget(i,0).text(), str(0)])
                add_row = []
                add_row.append(textbookid)
                add_row.append(self.category_combo_box.currentText())
                add_row.append(self.author_line_edit.text())
                add_row.append(self.title_line_edit.text())
                add_row.append(p.ordinal(self.edition_spin_box.value()))
                add_row.append(len(sections_list))
                add_row.append(None)
                add_row.append(self.num_chapters_spin_box.value())
                add_row.append(None)
                add_row.append(None)
                self.db_interface.insertEntry("Textbooks", tuple(add_row))
                self.console_text_edit.append(">> Added new textbook to database:")
                self.console_text_edit.append(">> Category: " + self.category_combo_box.currentText())
                self.console_text_edit.append(">> Author: " + self.author_line_edit.text())
                self.console_text_edit.append(">> Title: " + self.title_line_edit.text())
                self.console_text_edit.append(">> Edition: " + p.ordinal(self.edition_spin_box.value()))
                self.submitNewSections(textbookid, sections_list)
                self.createTextbookDir()
                self.console_text_edit.append("")
            else:
                pass
        else:
            pass


    def createTextbookDir(self):
        txtbk_dirname = self.author_line_edit.text() + " - " + self.title_line_edit.text()
        if p.ordinal(self.edition_spin_box.value()) != "1st":
            txtbk_dirname += " - " + p.ordinal(self.edition_spin_box.value())
        txtbk_dirpath = os.path.join(Config.MAIN_DIR, self.category_combo_box.currentText(), txtbk_dirname)
        textbook_dir = os.path.join(txtbk_dirpath, "Textbook")
        other_dir = os.path.join(txtbk_dirpath, "Other")
        solutions_manual_dir = os.path.join(txtbk_dirpath, "Solutions Manual")
        if not os.path.exists(txtbk_dirpath):
            os.mkdir(txtbk_dirpath)
        if not os.path.exists(textbook_dir):
            os.mkdir(textbook_dir)
        if not os.path.exists(other_dir):
            os.mkdir(other_dir)
        if not os.path.exists(solutions_manual_dir):
            os.mkdir(solutions_manual_dir)
        self.console_text_edit.append(">> Textbook directory created: " + str(txtbk_dirpath))
        if self.tb_file_path_line_edit.text() not in ['', None]:
            shutil.move(self.tb_file_path_line_edit.text(), textbook_dir)
            self.console_text_edit.append(">> " + self.tb_file_path_line_edit.text() + " moved to textbook directory.")
        if self.sm_file_path_line_edit.text() not in ['', None]:
            shutil.move(self.sm_file_path_line_edit.text(), solutions_manual_dir)
            self.console_text_edit.append(">> " + self.sm_file_path_line_edit.text() + " moved to textbook directory.")
        os.startfile(txtbk_dirpath)

    def clearFields(self):
        self.category_combo_box.setCurrentText("")
        self.author_line_edit.setText("")
        self.title_line_edit.setText("")
        self.edition_spin_box.setValue(0)
        self.tb_file_path_line_edit.setText("")
        self.sm_file_path_line_edit.setText("")
        self.num_chapters_spin_box.setValue(0)
        self.sections_check_box.setChecked(False)
        self.eoc_check_box.setChecked(False)
        for i in reversed(range(self.num_sections_table.rowCount())):
            self.num_sections_table.removeRow(i)
        self.console_text_edit.append(">> Fields cleared.")


    def generateCode(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))


