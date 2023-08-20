import ElementStyles
from ContentPages.ClassPage import Page
from CustomWidgets.ClassListWidget import ListWidget
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QHeaderView, QCheckBox
from PyQt5.QtGui import QFont, QCursor
import Config
import random
import string
from datetime import date



class AddToStudyListPage(Page):

    def __init__(self, ui,):
        Page.__init__(self, Config.AddToStudyListPage_page_number)
        self.ui = ui

    def objectReferences(self, db_interface, learning_page, exercise_page):
        self.db_interface = db_interface
        self.learning_page = learning_page
        self.exercise_page = exercise_page

    def showPage(self, exercises_to_be_added):
        self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
        self.exercises_to_be_added = exercises_to_be_added
        self.disconnectWidget(self.ui.add_new_study_list_pushbutton)
        self.ui.add_new_study_list_pushbutton.clicked.connect(lambda: self.addNewStudyList())
        self.disconnectWidget(self.ui.add_to_list_button)
        self.ui.add_to_list_button.clicked.connect(lambda: self.addToStudyList())
        self.disconnectWidget(self.ui.exit_button)
        self.ui.exit_button.clicked.connect(lambda: self.exitPage())
        #self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
        self.study_list_columns = self.db_interface.fetchColumnNames("Study Lists", [])
        self.ui.exercises_to_be_added_line_edit.setText("Number of exercises to be added: " + str(len(exercises_to_be_added)))
        self.setStudyListTable()
        self.ui.add_new_study_list_line_edit.clear()
        self.ui.content_pages.setCurrentIndex(self.page_number)

    def exitPage(self):
        # ex_nums = [entry["ExerciseNumber"] for entry in self.exercises_to_be_added]
        # popped_indices = [self.learning_page.textbook_exercises.index(entry) for entry in self.learning_page.textbook_exercises if entry["ExerciseNumber"] in ex_nums]
        #popped_indices = [self.learning_page.textbook_exercises.index(entry) for entry in self.exercises_to_be_added]
        # [self.learning_page.selected_exercises.pop(index) for index in popped_indices]
        #[self.learning_page.textbook_exercises.pop(index) for index in popped_indices]
        #for index, exercise in zip(popped_indices, self.exercises_to_be_added):
            #self.learning_page.selected_exercises.insert(index, exercise)
            #self.learning_page.textbook_exercises.insert(index, exercise)
        if len(self.exercises_to_be_added) == 1:
            for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
                self.ui.ex_study_list_tablewidget.removeRow(i)
            if self.exercises_to_be_added[0]["Tags"] is not None and len(self.exercises_to_be_added[0]["Tags"]) != 0:
                ex_study_lists = self.exercises_to_be_added[0]["Tags"].split(",")
                for i in range(len(ex_study_lists)):
                    self.ui.ex_study_list_tablewidget.insertRow(i)
                    self.ui.ex_study_list_tablewidget.setCellWidget(i, 0, QCheckBox())
                    study_list_label = [study_list["StudyListName"] for study_list in self.study_lists if study_list["StudyListID"] == ex_study_lists[i]][0]
                    self.ui.ex_study_list_tablewidget.setCellWidget(i, 1, QLabel(study_list_label))
                self.ui.ex_study_list_tablewidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.learning_page.study_lists = self.study_lists
        self.ui.content_pages.setCurrentIndex(self.learning_page.page_number)

    def setStudyListTable(self):
        for i in reversed(range(self.ui.study_list_tablewidget.rowCount())):
            self.ui.study_list_tablewidget.removeRow(i)
        self.ui.study_list_tablewidget.verticalHeader().setVisible(False)
        self.ui.study_list_tablewidget.setColumnCount(len(self.study_list_columns) + 1)
        self.ui.study_list_tablewidget.setHorizontalHeaderLabels([""] + self.study_list_columns)
        for i in range(len(self.study_lists)):
            self.ui.study_list_tablewidget.insertRow(i)
            self.ui.study_list_tablewidget.setCellWidget(i, 0, QCheckBox())
            self.ui.study_list_tablewidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            for j in range(len(self.study_list_columns)):
                self.ui.study_list_tablewidget.setCellWidget(i, j + 1, QLabel(self.study_lists[i][self.study_list_columns[j]]))
                self.ui.study_list_tablewidget.horizontalHeader().setSectionResizeMode(j + 1, QHeaderView.ResizeToContents)


    def addToStudyList(self):
        for i in range(self.ui.study_list_tablewidget.rowCount()):
            if self.ui.study_list_tablewidget.cellWidget(i, 0).isChecked():
                for ex in self.exercises_to_be_added:
                    if ex["Tags"] is None or ex["Tags"] == "":
                        ex["Tags"] = self.ui.study_list_tablewidget.cellWidget(i, 1).text()
                    elif self.ui.study_list_tablewidget.cellWidget(i, 1).text() not in ex["Tags"].split(","):
                        ex["Tags"] = ",".join([ex["Tags"], self.ui.study_list_tablewidget.cellWidget(i, 1).text()])
                    update_list = [ex["Tags"], ex["TextbookID"], ex["ExerciseID"]]
                    self.db_interface.updateEntry("Update Exercise Tag", update_list)
        self.exitPage()

    def addNewStudyList(self):
        while self.ui.add_to_list_button.isDown():
            continue
        if self.ui.add_new_study_list_line_edit.text() is not None and len(self.ui.add_new_study_list_line_edit.text()) != 0:
            if self.ui.add_new_study_list_line_edit.text() not in [study_list["StudyListName"] for study_list in self.study_lists]:
                new_tag = self.generateCode()
                new_list_tuple = (new_tag, self.ui.add_new_study_list_line_edit.text(), date.today().strftime("%m/%d/%Y"))
                #self.study_lists.append(dict(zip(self.study_list_columns, list(new_list_tuple))))
                self.db_interface.insertEntry("Study List", new_list_tuple)

                all_tags = ""
                uncat_collection = self.db_interface.fetchEntries("Study List Collection", [str(00000)])[0]
                if uncat_collection["Tags"] is None or uncat_collection["Tags"] == "":
                    all_tags = new_tag
                elif new_tag not in uncat_collection["Tags"].split(","):
                    all_tags = ",".join([uncat_collection["Tags"], new_tag])
                update_list = [all_tags, uncat_collection["CollectionID"]]
                self.db_interface.updateEntry("Update SL Collection Tags", update_list)

                self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
        self.showPage(self.exercises_to_be_added)

    def generateCode(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))


