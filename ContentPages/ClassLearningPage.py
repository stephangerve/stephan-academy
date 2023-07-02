import ElementStyles
from ContentPages.ClassPage import Page
from UIElements import ListElement
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QHeaderView, QCheckBox, QApplication, QListWidget
from PyQt5.QtGui import QFont, QCursor
import Config


class LearningPage(Page):
    ui = None
    db_interface = None
    exercise_page = None
    category_page = None
    #query_table_names = None
    #table_index = None
    category_textbooks = None
    textbook_sections = None

    selected_exercises = None
    selected_textbook_ID = None
    selected_category = None
    selected_author = None
    selected_textbook_title = None
    selected_edition = None
    selected_chap_num = None
    selected_sect_num = None


    def __init__(self, ui, ):
        Page.__init__(self, Config.LearningPage_page_number)
        self.ui = ui
        #self.query_table_names = ["Textbooks", "Sections", "Exercises"]
        #self.table_index = 0
        self.textbooks_list_element = ListElement(self.ui.textbooks_listwidget)
        self.sections_list_element = ListElement(self.ui.sections_listwidget)
        self.prev_selected_exercise_num = None
        self.prev_selected_exercise_bgcolor = None
        self.prev_textbook_lw_index = None
        self.prev_section_lw_index = None


    def objectReferences(self, db_interface, exercise_page, category_page, add_textbook_page, add_exercises_page, add_to_study_list_page, study_lists):
        self.exercise_page = exercise_page
        self.db_interface = db_interface
        self.category_page = category_page
        self.add_textbook_page = add_textbook_page
        self.add_exercises_page = add_exercises_page
        self.add_to_study_list_page = add_to_study_list_page
        self.study_lists = study_lists
        #self.connectButtons()
        #self.currently_selected = -1

    def showPage(self, cat_str):
        self.clearPage()
        ElementStyles.regularShadow(self.ui.textbook_info_frame_left)
        ElementStyles.regularShadow(self.ui.ex_stats_info)
        ElementStyles.regularShadow(self.ui.sb_frame)
        ElementStyles.lightShadow(self.ui.start_button)
        ElementStyles.regularShadow(self.ui.mode_frame)
        ElementStyles.regularShadow(self.ui.grade_filter_frame)
        ElementStyles.regularShadow(self.ui.sl_frame)
        self.ui.sb_frame.setStyleSheet("background-color: grey")
        self.ui.start_button.setStyleSheet("color: black")
        self.ui.start_button.setEnabled(False)
        self.prev_textbook_lw_index = None
        self.prev_section_lw_index = None
        self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
        self.selected_category = cat_str
        self.category_textbooks = self.db_interface.fetchEntries("Textbooks", [self.selected_category])
        self.textbooks_list_element.setList("Textbooks", self.category_textbooks)
        self.disconnectWidget(self.ui.textbooks_listwidget)
        self.ui.textbooks_listwidget.itemClicked.connect(lambda: self.textbookEntryClicked(int(self.ui.textbooks_listwidget.currentItem().text())))
        self.disconnectWidget(self.ui.back_button)
        self.ui.back_button.clicked.connect(lambda: self.category_page.showPage())
        self.disconnectWidget(self.ui.add_new_textbook_button)
        self.ui.add_new_textbook_button.clicked.connect(lambda: self.add_textbook_page.showPage(cat_str))
        self.ui.content_pages.setCurrentIndex(self.page_number)


    def clearPage(self):
        self.clearExercisesGrid()
        self.ui.category_info_label.clear()
        self.ui.textbook_info_label.clear()
        self.ui.chapter_info_label.clear()
        self.ui.section_info_label.clear()
        self.ui.ex_stats_info_grade_label.clear()
        self.ui.ex_stats_info_lastattempt_label.clear()
        self.ui.ex_stats_info_totalattempts_label.clear()
        self.ui.ex_stats_info_averagetime_label.clear()
        self.textbooks_list_element.clear()
        self.sections_list_element.clear()


    def textbookEntryClicked(self, ui_list_index):
        self.ui.sb_frame.setStyleSheet("background-color: gray")
        self.ui.start_button.setStyleSheet("color: black")
        self.ui.start_button.setEnabled(False)
        self.sections_list_element.clear()
        self.ui.chapter_info_label.clear()
        self.ui.section_info_label.clear()
        ElementStyles.selectedListItem(self.ui.textbooks_listwidget.itemWidget(self.ui.textbooks_listwidget.currentItem()))
        if self.prev_textbook_lw_index is not None:
            ElementStyles.unselectedListItem(self.ui.textbooks_listwidget.itemWidget(self.ui.textbooks_listwidget.item(self.prev_textbook_lw_index)))
        self.prev_textbook_lw_index = ui_list_index - 1
        self.prev_section_lw_index = None
        self.clearExercisesGrid()
        self.selected_textbook_ID = self.category_textbooks[ui_list_index - 1]["TextbookID"]
        self.textbook_sections = self.db_interface.fetchEntries("Sections", [self.selected_textbook_ID])
        self.selected_author = self.category_textbooks[ui_list_index - 1]["Authors"]
        self.selected_textbook_title = self.category_textbooks[ui_list_index - 1]["Title"]
        self.selected_edition = self.category_textbooks[ui_list_index - 1]["Edition"]
        self.ui.category_info_label.setText(str(self.selected_category))
        self.ui.textbook_info_label.setText(" - ".join([self.selected_author, self.selected_textbook_title, self.selected_edition]))
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.textbook_exercises = self.db_interface.fetchEntries("Textbook Exercises", [self.selected_textbook_ID])
        QApplication.restoreOverrideCursor()
        self.updateSectionList()
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)
        self.disconnectWidget(self.ui.sections_listwidget)
        self.ui.sections_listwidget.itemClicked.connect(lambda: self.sectionsEntryClicked(int(self.ui.sections_listwidget.currentItem().text())))
        if len(self.textbook_exercises) > 0:
            for i in range(self.ui.sections_listwidget.count()):
                chap_num = self.textbook_sections[i]["ChapterNumber"]
                sect_num = self.textbook_sections[i]["SectionNumber"]
                exercises = [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == chap_num and entry["SectionNumber"] == sect_num]
                if len(exercises) > 0:
                    num = int(exercises[0]["ExerciseID"].split(".")[-1])
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-3].clicked.connect(lambda state, num=num, exercises=exercises: self.exercise_page.showPage(num, exercises))
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-1].clicked.connect(lambda state, exercises_to_be_added=exercises: self.add_to_study_list_page.showPage(exercises_to_be_added))
            self.disconnectWidget(self.ui.add_new_exercises_button)
            self.ui.add_new_exercises_button.clicked.connect(lambda: self.add_exercises_page.showPage(self.textbook_sections, self.selected_textbook_ID, self.selected_category, self.selected_author, self.selected_textbook_title, self.selected_edition))

    def updateSectionList(self):
        for sect_entry in self.textbook_sections:
            sect_entry["NumExercisesA"] = sum([1 for entry in self.textbook_exercises if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"] and entry["Grade"] == 'A'])
            sect_entry["NumExercisesB"] = sum([1 for entry in self.textbook_exercises if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"] and entry["Grade"] == 'B'])
            sect_entry["NumExercisesC"] = sum([1 for entry in self.textbook_exercises if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"] and entry["Grade"] == 'C'])
            sect_entry["NumExercisesD"] = sum([1 for entry in self.textbook_exercises if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"] and entry["Grade"] == 'D'])
            sect_entry["NumExercisesF"] = sum([1 for entry in self.textbook_exercises if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"] and entry["Grade"] == 'F'])
            sect_entry["NoGrade"] = sum([1 for entry in self.textbook_exercises if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"] and entry["SolutionExists"] == 'True' and entry["Attempts"] == 0])
        self.sections_list_element.setList("Sections", self.textbook_sections)

    def sectionsEntryClicked(self, ui_list_index):
        self.ui.sb_frame.setStyleSheet("background-color: gray")
        self.ui.start_button.setStyleSheet("color: black")
        self.ui.start_button.setEnabled(False)
        ElementStyles.selectedListItem(self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.currentItem()))
        if self.prev_section_lw_index is not None:
            ElementStyles.unselectedListItem(self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(self.prev_section_lw_index)))
        self.prev_section_lw_index = ui_list_index - 1
        self.selected_chap_num = self.textbook_sections[ui_list_index - 1]["ChapterNumber"]
        self.selected_sect_num = self.textbook_sections[ui_list_index - 1]["SectionNumber"]
        #self.selected_exercises = self.db_interface.fetchEntries("Exercises", [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num])
        self.selected_exercises = [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == self.selected_chap_num and entry["SectionNumber"] == self.selected_sect_num]
        self.setExercisesButtons()
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)



    def highlightSelectedItemWidget(self, item_selected):
        if int(item_selected.text()) != self.currently_selected:
            widget = self.ListElementWidget(int(item_selected.text()), True)
            self.ui.textbooks_listwidget.setItemWidget(item_selected, widget)
            if self.currently_selected != -1:
                item_previous = (self.ui.textbooks_listwidget.findItems(str(self.currently_selected), QtCore.Qt.MatchExactly))[0]
                widget = self.ListElementWidget(int(item_previous.text()), False)
                self.ui.textbooks_listwidget.setItemWidget(item_previous, widget)
            self.currently_selected = int(item_selected.text())

    def ListElementWidget(self, item_selected, highlight):
        entry_id = self.cameras.cam_ids[item_selected - 1]
        # Cam id label
        entryIDLabel = QLabel()
        entryIDLabel.setText(str(entry_id))



        entryIDLabel.setFixedWidth(108)


        # Add widgets
        elementLayout = QHBoxLayout()


        if highlight is True:
            entryIDLabel.setStyleSheet("color: white")

            rowLabel = QLabel()
            elementLayout.addStretch()
            elementLayout.addWidget(rowLabel)

            elementLayout.setContentsMargins(5, 5, 5, 5)
            elementLayout.setSpacing(0)

            widget = QWidget()
            widget.setLayout(elementLayout)
            widget.setStyleSheet("background-color: rgb(187, 194, 202)")
            ElementStyles.lightShadow(widget)
        elif highlight is False:
            entryIDLabel.setStyleSheet("color: #4e5256")

            rowLabel = QLabel()
            elementLayout.addStretch()
            elementLayout.addWidget(rowLabel)

            elementLayout.setContentsMargins(5, 5, 5, 5)
            elementLayout.setSpacing(0)

            widget = QWidget()
            widget.setLayout(elementLayout)
            widget.setStyleSheet("background-color: #ffffff")

        return widget

    def clearExercisesGrid(self):
        for i in reversed(range(self.ui.exercises_grid.count())):
            self.ui.exercises_grid.itemAt(i).widget().setParent(None)

    def setExercisesButtons(self):
        self.prev_selected_exercise_num = None
        self.clearExercisesGrid()
        self.ui.chapter_info_label.setText(str(self.selected_chap_num))
        self.ui.section_info_label.setText(str(self.selected_sect_num))
        count = len(self.selected_exercises)
        if count > 0:
            if count % 10 == 0:
                rows = int(count / 10)
            else:
                rows = int(count / 10) + 1
            for i in range(rows):
                if int(count / ((i + 1) * 10)) > 0:
                    columns = 10
                elif i > 0:
                    columns = count % (i * 10)
                else:
                    columns = count
                for j in range(columns):
                    index = i * 10 + j
                    ex_num = int(self.selected_exercises[index]["ExerciseID"].split(".")[-1])
                    self.button = QPushButton(str(ex_num))
                    self.button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                    self.button.setCheckable(True)
                    ElementStyles.lightShadow(self.button)
                    #if self.db_interface.fetchBool("SolutionExists", [exercises[index]["TextbookID"], exercises[index]["ExerciseID"]]) is True:
                    if self.selected_exercises[index]["SolutionExists"] is not None:
                        if eval(self.selected_exercises[index]["SolutionExists"]):
                            if eval(self.selected_exercises[index]["Seen"]):
                                grade = self.selected_exercises[index]["Grade"]
                                if grade in Config.EXERCISE_GRADE_COLORS.keys():
                                    color = "rgb" + str(Config.EXERCISE_GRADE_COLORS[grade])
                                else:
                                    color = "gray"
                            else:
                                color = "white"
                            self.disconnectWidget(self.button)
                            self.button.clicked.connect(lambda state, exnum=int(self.button.text()): self.showExerciseStats(exnum))
                        else:
                            color = "lightgray"
                            self.button.toggle()
                            self.button.setEnabled(False)
                    else:
                        color = "lightgray"
                        self.button.toggle()
                        self.button.setEnabled(False)
                    self.button.setStyleSheet("background-color : " + color)
                    self.ui.exercises_grid.addWidget(self.button, i, j)
        else:
            label = QLabel("\n\n\n\n\nNo Exercises!")
            color = "white"
            label.setStyleSheet("background-color : " + color)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFont(QFont("Arial", 12))
            label.resize(60, 80)
            self.ui.exercises_grid.addWidget(label, 0, 0)

    def showExerciseStats(self, num):
        self.ui.sb_frame.setStyleSheet("background-color: rgb(0, 170, 127)")
        self.ui.start_button.setStyleSheet("color: white")
        self.ui.start_button.setEnabled(True)
        if self.prev_selected_exercise_num is not None:
            last_grid_index = [self.selected_exercises.index(entry) for entry in self.selected_exercises if int(entry["ExerciseID"].split(".")[-1]) == self.prev_selected_exercise_num][0]
            self.ui.exercises_grid.itemAt(last_grid_index).widget().setEnabled(True)
            self.ui.exercises_grid.itemAt(last_grid_index).widget().toggle()
            self.ui.exercises_grid.itemAt(last_grid_index).widget().setStyleSheet("background-color : " + self.prev_selected_exercise_bgcolor)
        grid_index, self.exercise_stats = [[self.selected_exercises.index(entry), entry] for entry in self.selected_exercises if int(entry["ExerciseID"].split(".")[-1]) == num][0]
        self.prev_selected_exercise_num = num
        self.ui.exercises_grid.itemAt(grid_index).widget().setEnabled(False)
        self.ui.exercises_grid.itemAt(grid_index).widget().setStyleSheet("background-color : lightblue")
        if eval(self.exercise_stats["Seen"]) and self.exercise_stats["Attempts"] > 0:
            self.ui.ex_stats_info_grade_label.setText(str(self.exercise_stats["Grade"]))
            self.ui.ex_stats_info_lastattempt_label.setText(str(self.exercise_stats["LastAttempted"]) + " -- " + str(self.exercise_stats["LastAttemptTime"]))
            self.ui.ex_stats_info_totalattempts_label.setText(str(self.exercise_stats["Attempts"]))
            self.ui.ex_stats_info_averagetime_label.setText(str(self.exercise_stats["AverageTime"]))
            self.prev_selected_exercise_bgcolor = "rgb" + str(Config.EXERCISE_GRADE_COLORS[self.exercise_stats["Grade"]])
        elif eval(self.exercise_stats["Seen"]) and self.exercise_stats["Attempts"] == 0:
            self.ui.ex_stats_info_grade_label.setText("N/A")
            self.ui.ex_stats_info_lastattempt_label.setText("N/A")
            self.ui.ex_stats_info_totalattempts_label.setText("N/A")
            self.ui.ex_stats_info_averagetime_label.setText("N/A")
            self.prev_selected_exercise_bgcolor = "gray"
        else:
            self.ui.ex_stats_info_grade_label.setText("N/A")
            self.ui.ex_stats_info_lastattempt_label.setText("N/A")
            self.ui.ex_stats_info_totalattempts_label.setText("N/A")
            self.ui.ex_stats_info_averagetime_label.setText("N/A")
            self.prev_selected_exercise_bgcolor = "white"
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)
        self.setStudyListTable()
        self.disconnectWidget(self.ui.start_button)
        self.disconnectWidget(self.ui.add_to_a_study_list_button)
        self.disconnectWidget(self.ui.remove_from_a_study_list_button)
        self.ui.start_button.clicked.connect(lambda state, num=num, exercises=self.selected_exercises: self.exercise_page.showPage(num, exercises))
        self.ui.add_to_a_study_list_button.clicked.connect(lambda state, exercises_to_be_added=[self.exercise_stats]: self.add_to_study_list_page.showPage(exercises_to_be_added))
        self.ui.remove_from_a_study_list_button.clicked.connect(lambda: self.removeFromStudyList())

    def setStudyListTable(self):
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)
        self.ui.ex_study_list_tablewidget.verticalHeader().setVisible(False)
        self.ui.ex_study_list_tablewidget.setColumnCount(2)
        self.ui.ex_study_list_tablewidget.setHorizontalHeaderLabels(["", "Study Lists"])
        self.ui.ex_study_list_tablewidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        if self.exercise_stats["Tags"] is not None and len(self.exercise_stats["Tags"]) != 0:
            ex_study_lists = self.exercise_stats["Tags"].split(",")
            for i in range(len(ex_study_lists)):
                self.ui.ex_study_list_tablewidget.insertRow(i)
                self.ui.ex_study_list_tablewidget.setCellWidget(i, 0, QCheckBox())
                study_list_label = [study_list["StudyListName"] for study_list in self.study_lists if study_list["StudyListID"] == ex_study_lists[i]][0]
                self.ui.ex_study_list_tablewidget.setCellWidget(i, 1, QLabel(study_list_label))
            self.ui.ex_study_list_tablewidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def removeFromStudyList(self):
        popped_index = [self.selected_exercises.index(entry) for entry in self.selected_exercises if entry["ExerciseNumber"] == self.exercise_stats["ExerciseNumber"]][0]
        self.selected_exercises.pop(popped_index)
        for i in range(self.ui.ex_study_list_tablewidget.rowCount()):
            if self.ui.ex_study_list_tablewidget.cellWidget(i, 0).isChecked():
                study_list_id = [study_list["StudyListID"] for study_list in self.study_lists if study_list["StudyListName"] == self.ui.ex_study_list_tablewidget.cellWidget(i, 1).text()][0]
                tags = self.exercise_stats["Tags"].split(",")
                tags.pop(tags.index(study_list_id))
                if tags is not None:
                    self.exercise_stats["Tags"] = ",".join(tags)
                else:
                    self.exercise_stats["Tags"] = None
                update_tuple = (self.exercise_stats["Tags"], self.exercise_stats["TextbookID"], self.exercise_stats["ExerciseID"])
                self.db_interface.updateEntry("Update Exercise Tag", update_tuple)
        self.selected_exercises.insert(popped_index, self.exercise_stats)
        self.setStudyListTable()


# self.ui.textbooks_listwidget.takeItem(ui_list_index - 1)
# entry = self.category_textbooks[ui_list_index - 1]
# elementLayout = QHBoxLayout()
# authorLabel = QLabel()
# authorLabel.setText(entry["Authors"])
# authorLabel.setFixedWidth(80)
# authorLabel.setStyleSheet("color: #ffffff")
# elementLayout.addWidget(authorLabel)
# titleLabel = QLabel()
# titleLabel.setText(entry["Title"])
# titleLabel.setFixedWidth(320)
# titleLabel.setStyleSheet("color: #ffffff")
# elementLayout.addWidget(titleLabel)
# edLabel = QLabel()
# edLabel.setText(entry["Edition"])
# edLabel.setStyleSheet("color: #ffffff")
# elementLayout.addWidget(edLabel)
# rowLabel = QLabel()
# elementLayout.addStretch()
# elementLayout.addWidget(rowLabel)
# elementLayout.setContentsMargins(5, 5, 5, 5)
# elementLayout.setSpacing(0)
# widget = QWidget()
# widget.setLayout(elementLayout)
# ElementStyles.whiteRoundSquare(widget)
# ElementStyles.navyBlueBackground(widget)
# qlistwidget = QListWidgetItem()
# self.ui.textbooks_listwidget.insertItem(ui_list_index - 1, qlistwidget)
# self.ui.textbooks_listwidget.setItemWidget(qlistwidget, widget)
