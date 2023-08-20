import ElementStyles
from ContentPages.ClassPage import Page
from CustomWidgets.ClassListWidget import ListWidget
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QHeaderView, QCheckBox, QApplication, QListWidget
from PyQt5.QtGui import QFont, QCursor
import Config
from datetime import datetime


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
        self.textbooks_list_element = ListWidget(self.ui.textbooks_listwidget)
        self.sections_list_element = ListWidget(self.ui.sections_listwidget)
        self.prev_selected_exercise_num = None
        self.prev_selected_exercise_bgcolor = None
        self.prev_textbook_lw_index = None
        self.prev_section_list_item_widget = None
        self.add_new_exercises_button = None
        self.add_sections_button = None
        self.add_sections_to_sl_button = None
        self.CN_sort_order = None
        self.SN_sort_order = None
        self.count_sort_order = None
        self.progress_sort_order = None


    def objectReferences(self, db_interface, exercise_page, category_page, add_textbook_page, add_exercises_page, add_to_study_list_page):
        self.exercise_page = exercise_page
        self.db_interface = db_interface
        self.category_page = category_page
        self.add_textbook_page = add_textbook_page
        self.add_exercises_page = add_exercises_page
        self.add_to_study_list_page = add_to_study_list_page
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
        self.prev_section_list_item_widget = None
        self.sections_selected_count = 0
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
        self.ui.date_filter_button.clicked.connect(lambda: self.setDateFilter())
        self.setDateFilter()
        self.clearSectionActionButtonLayout()
        self.ui.content_pages.setCurrentIndex(self.page_number)

    def setDateFilter(self):
        parsed_date = [str(l).zfill(2) if len(str(l)) == 1 else str(l) for l in list(self.ui.date_filter_edit.date().getDate())]
        self.date_filter = "/".join([parsed_date[1], parsed_date[2], parsed_date[0]])
        if self.prev_textbook_lw_index is not None:
            self.updateSectionList()
        self.prev_section_list_item_widget = None
        self.clearExercisesGrid()


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

    def clearSectionActionButtonLayout(self):
        try: self.add_new_exercises_button.clicked.disconnect()
        except: pass
        try: self.add_new_exercises_button.clicked.disconnect()
        except: pass
        for i in reversed(range(self.ui.section_action_button_layout.count())):
            self.ui.section_action_button_layout.itemAt(i).widget().setParent(None)


    def textbookEntryClicked(self, ui_list_index):
        self.CN_sort_order = None
        self.SN_sort_order = None
        self.count_sort_order = None
        self.progress_sort_order = None
        self.ui.sb_frame.setStyleSheet("background-color: gray")
        self.ui.start_button.setStyleSheet("color: black")
        self.ui.start_button.setEnabled(False)
        self.sections_list_element.clear()
        self.ui.chapter_info_label.clear()
        self.ui.section_info_label.clear()
        self.sections_selected_count = 0
        ElementStyles.selectedListItem(self.ui.textbooks_listwidget.itemWidget(self.ui.textbooks_listwidget.currentItem()))
        if self.prev_textbook_lw_index is not None:
            ElementStyles.unselectedListItem(self.ui.textbooks_listwidget.itemWidget(self.ui.textbooks_listwidget.item(self.prev_textbook_lw_index)))
        self.prev_textbook_lw_index = ui_list_index - 1
        self.prev_section_list_item_widget = None
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
        if len(self.textbook_exercises) > 0:
            count_dict = {}
            for entry in self.textbook_exercises:
                if entry["ChapterNumber"] not in count_dict.keys():
                    count_dict[entry["ChapterNumber"]] = {}
                if entry["SectionNumber"] not in count_dict[entry["ChapterNumber"]].keys():
                    count_dict[entry["ChapterNumber"]][entry["SectionNumber"]] = 0
                if entry["SolutionExists"] != "None" and entry["SolutionExists"] is not None and entry["SolutionExists"] != "":
                    if eval(entry["SolutionExists"]):
                        count_dict[entry["ChapterNumber"]][entry["SectionNumber"]] += 1
        for sect_entry in self.textbook_sections:
            if len(self.textbook_exercises) > 0 and sect_entry["ChapterNumber"] in count_dict.keys() and sect_entry["SectionNumber"] in count_dict[sect_entry["ChapterNumber"]].keys():
                sect_entry["Count"] = count_dict[sect_entry["ChapterNumber"]][sect_entry["SectionNumber"]]
            else:
                sect_entry["Count"] = 0
        self.textbook_sections = sorted(self.textbook_sections,
                                        key=lambda x: (int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999, int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999))
        QApplication.restoreOverrideCursor()
        self.updateSectionList()
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)
        self.disconnectWidget(self.ui.sections_listwidget)
        self.ui.sections_listwidget.itemClicked.connect(lambda: self.sectionsEntryClicked(self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.currentItem())))
        if len(self.textbook_exercises) > 0:
            for i in range(self.ui.sections_listwidget.count()):
                chap_num = self.textbook_sections[i]["ChapterNumber"]
                sect_num = self.textbook_sections[i]["SectionNumber"]
                exercises = [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == chap_num and entry["SectionNumber"] == sect_num]
                if len(exercises) > 0:
                    num = int(exercises[0]["ExerciseID"].split(".")[-1])
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-3].clicked.connect(lambda state, num=num, exercises=exercises: self.exercise_page.showPage(num, exercises))
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-1].clicked.connect(lambda state, exercises_to_be_added=exercises: self.add_to_study_list_page.showPage(exercises_to_be_added))
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[1].stateChanged.connect(lambda state, i=i: self.multipleSectionsSelected(self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i))))
        self.addButtonsToSectionActionButtonsLayout()
        self.disconnectWidget(self.ui.select_all_sections_checkbox)
        self.disconnectWidget(self.ui.CN_sort_button)
        self.disconnectWidget(self.ui.SN_sort_button)
        self.disconnectWidget(self.ui.count_sort_button)
        self.disconnectWidget(self.ui.progress_sort_button)
        self.ui.select_all_sections_checkbox.setCheckState(False)
        self.ui.select_all_sections_checkbox.stateChanged.connect(lambda: self.selectAllSections(self.ui.select_all_sections_checkbox.checkState()))
        self.ui.CN_sort_button.clicked.connect(lambda: self.sortSectionsListBy("ChapterNumber"))
        self.ui.SN_sort_button.clicked.connect(lambda: self.sortSectionsListBy("SectionNumber"))
        self.ui.count_sort_button.clicked.connect(lambda: self.sortSectionsListBy("Count"))
        self.ui.progress_sort_button.clicked.connect(lambda: self.sortSectionsListBy("Progress"))


    def addButtonsToSectionActionButtonsLayout(self):
        self.clearSectionActionButtonLayout()
        if self.add_sections_button is None:
            self.add_sections_button = QPushButton("Add Sections")
            self.add_sections_button.setCursor(Qt.PointingHandCursor)
            self.add_sections_button.setStyleSheet("color: white")
        self.ui.section_action_button_layout.addWidget(self.add_sections_button)
        self.disconnectWidget(self.add_sections_button)
        if self.add_new_exercises_button is None:
            self.add_new_exercises_button = QPushButton("Add New Exercises")
            self.add_new_exercises_button.setCursor(Qt.PointingHandCursor)
            self.add_new_exercises_button.setStyleSheet("color: white")
        self.ui.section_action_button_layout.addWidget(self.add_new_exercises_button)
        self.disconnectWidget(self.add_new_exercises_button)
        self.add_new_exercises_button.clicked.connect(lambda: self.add_exercises_page.showPage(self.textbook_sections, self.selected_textbook_ID, self.selected_category, self.selected_author, self.selected_textbook_title, self.selected_edition))


    def selectAllSections(self, state):
        for i in range(self.ui.sections_listwidget.count()):
            item_widget = self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i))
            self.disconnectWidget(item_widget.children()[1])
            if state:
                if not item_widget.children()[1].isChecked():
                    item_widget.children()[1].setChecked(True)
                    self.sections_selected_count += 1
                    ElementStyles.highlightListItem(item_widget)
            else:
                if item_widget.children()[1].isChecked():
                    item_widget.children()[1].setChecked(False)
                    self.sections_selected_count -= 1
                    ElementStyles.unselectedListItem(item_widget)
            item_widget.children()[1].stateChanged.connect(lambda state, item_widget=item_widget: self.multipleSectionsSelected(item_widget))

        if self.sections_selected_count > 0:
            self.clearSectionActionButtonLayout()
            if self.add_sections_to_sl_button is None:
                self.add_sections_to_sl_button = QPushButton("Add Sections to Study List")
                self.add_sections_to_sl_button.setCursor(Qt.PointingHandCursor)
                self.add_sections_to_sl_button.setStyleSheet("color: white")
            self.ui.section_action_button_layout.addWidget(self.add_sections_to_sl_button)
            self.disconnectWidget(self.add_sections_to_sl_button)
            exercises = []
            for i in range(self.ui.sections_listwidget.count()):
                item_widget = self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i))
                if item_widget.children()[1].isChecked():
                    chap_num = item_widget.children()[3].text()
                    sect_num = item_widget.children()[4].text()
                    exercises += [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == chap_num and entry["SectionNumber"] == sect_num]
            self.add_sections_to_sl_button.clicked.connect(lambda state, exercises_to_be_added=exercises: self.add_to_study_list_page.showPage(exercises_to_be_added))
        else:
            self.addButtonsToSectionActionButtonsLayout()


    def multipleSectionsSelected(self, item_widget):
        if item_widget.children()[1].isChecked() and self.sections_selected_count < self.ui.sections_listwidget.count():
            self.sections_selected_count += 1
            ElementStyles.highlightListItem(item_widget)
        else:
            self.sections_selected_count -= 1
            ElementStyles.unselectedListItem(item_widget)
        if self.sections_selected_count > 0:
            self.clearSectionActionButtonLayout()
            if self.add_sections_to_sl_button is None:
                self.add_sections_to_sl_button = QPushButton("Add Sections to Study List")
                self.add_sections_to_sl_button.setCursor(Qt.PointingHandCursor)
                self.add_sections_to_sl_button.setStyleSheet("color: white")
            self.ui.section_action_button_layout.addWidget(self.add_sections_to_sl_button)
            self.disconnectWidget(self.add_sections_to_sl_button)
            exercises = []
            for i in range(self.ui.sections_listwidget.count()):
                item_widget = self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i))
                if item_widget.children()[1].isChecked():
                    chap_num = item_widget.children()[3].text()
                    sect_num = item_widget.children()[4].text()
                    exercises += [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == chap_num and entry["SectionNumber"] == sect_num]
            self.add_sections_to_sl_button.clicked.connect(lambda state, exercises_to_be_added=exercises: self.add_to_study_list_page.showPage(exercises_to_be_added))
        else:
            self.addButtonsToSectionActionButtonsLayout()


    def updateSectionList(self):
        for sect_entry in self.textbook_sections:
            sect_entry["NumExercisesA"] = 0
            sect_entry["NumExercisesB"] = 0
            sect_entry["NumExercisesC"] = 0
            sect_entry["NumExercisesD"] = 0
            sect_entry["NumExercisesF"] = 0
            sect_entry["NoGrade"] = 0
            for entry in self.textbook_exercises:
                if entry["ChapterNumber"] == sect_entry["ChapterNumber"] and entry["SectionNumber"] == sect_entry["SectionNumber"]:
                    if entry["Attempts"] > 0:
                        if datetime.strptime(entry["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
                            if entry["Grade"] == 'A':
                                sect_entry["NumExercisesA"] += 1
                            elif entry["Grade"] == 'B':
                                sect_entry["NumExercisesB"] += 1
                            elif entry["Grade"] == 'C':
                                sect_entry["NumExercisesC"] += 1
                            elif entry["Grade"] == 'D':
                                sect_entry["NumExercisesD"] += 1
                            elif entry["Grade"] == 'F':
                                sect_entry["NumExercisesF"] += 1
                        else:
                            sect_entry["NoGrade"] += 1
                    elif entry["SolutionExists"] == 'True':
                        sect_entry["NoGrade"] += 1
        self.sections_list_element.setList("Sections", self.textbook_sections)

        if self.prev_section_list_item_widget is not None:
            for i in range(self.ui.sections_listwidget.count()):
                if self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[3].text() == self.prev_section_list_item_widget.children()[3].text():
                    if self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[4].text() == self.prev_section_list_item_widget.children()[4].text():
                        if self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[5].text() == self.prev_section_list_item_widget.children()[5].text():
                            self.prev_section_list_item_widget = self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i))
                            break
            self.sectionsEntryClicked(self.prev_section_list_item_widget)

    def sectionsEntryClicked(self, item_widget):
        self.ui.sb_frame.setStyleSheet("background-color: gray")
        self.ui.start_button.setStyleSheet("color: black")
        self.ui.start_button.setEnabled(False)
        if self.prev_section_list_item_widget is not None:
            if self.prev_section_list_item_widget.children()[1].isChecked():
                ElementStyles.highlightListItem(self.prev_section_list_item_widget)
            else:
                ElementStyles.unselectedListItem(self.prev_section_list_item_widget)
        ElementStyles.selectedListItem(item_widget)
        self.prev_section_list_item_widget = item_widget
        self.selected_chap_num = [entry["ChapterNumber"] for entry in self.textbook_sections if entry["ChapterNumber"] == item_widget.children()[3].text()][0]
        self.selected_sect_num = [entry["SectionNumber"] for entry in self.textbook_sections if entry["SectionNumber"] == item_widget.children()[4].text()][0]
        #self.selected_exercises = self.db_interface.fetchEntries("Exercises", [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num])
        self.selected_exercises = [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == self.selected_chap_num and entry["SectionNumber"] == self.selected_sect_num]
        self.setExercisesButtons()
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)



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
                                if grade in Config.EXERCISE_GRADE_COLORS.keys() and datetime.strptime(self.selected_exercises[index]["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
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
            if datetime.strptime(self.exercise_stats["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
                self.prev_selected_exercise_bgcolor = "rgb" + str(Config.EXERCISE_GRADE_COLORS[self.exercise_stats["Grade"]])
            else:
                self.prev_selected_exercise_bgcolor = "gray"
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

    def sortSectionsListBy(self, column):
        if column == "ChapterNumber":
            self.SN_sort_order = 1
            self.count_sort_order = None
            self.progress_sort_order = None
            if self.CN_sort_order is None or self.CN_sort_order == -1:
                self.CN_sort_order = 1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: (int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999, int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999), reverse=True)
            elif self.CN_sort_order == 1:
                self.CN_sort_order = -1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: (int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999, int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999))
        elif column == "SectionNumber":
            self.CN_sort_order = 1
            self.count_sort_order = None
            self.progress_sort_order = None
            if self.SN_sort_order is None or self.SN_sort_order == -1:
                self.SN_sort_order = 1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: (int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999, int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999), reverse=True)
            elif self.SN_sort_order == 1:
                self.SN_sort_order = -1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: (int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999, int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999))
        elif column == "Count":
            self.CN_sort_order = 1
            self.SN_sort_order = 1
            self.progress_sort_order = None
            if self.count_sort_order is None or self.count_sort_order == -1:
                self.count_sort_order = 1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: x['Count'], reverse=True)
            elif self.count_sort_order == 1:
                self.count_sort_order = -1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: x['Count'])
        elif column == "Progress":
            self.CN_sort_order = 1
            self.SN_sort_order = 1
            self.count_sort_order = None
            for sect_entry in self.textbook_sections:
                if sect_entry["Count"] > 0:
                    weighted_count_A = sect_entry["NumExercisesA"] * 5
                    weighted_count_B = sect_entry["NumExercisesB"] * 4
                    weighted_count_C = sect_entry["NumExercisesC"] * 3
                    weighted_count_D = sect_entry["NumExercisesD"] * 2
                    weighted_count_F = sect_entry["NumExercisesF"] * 1
                    sect_entry["Progress"] = \
                        (weighted_count_A + weighted_count_B + weighted_count_C + weighted_count_D + weighted_count_F) / (sect_entry["Count"] * 5)
                else:
                    sect_entry["Progress"] = 0.0
            if self.progress_sort_order is None or self.progress_sort_order == 1:
                self.progress_sort_order = -1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: x['Progress'])
            elif self.progress_sort_order == -1:
                self.progress_sort_order = 1
                self.textbook_sections = sorted(self.textbook_sections, key=lambda x: x['Progress'], reverse=True)



        self.sections_list_element.setList("Sections", self.textbook_sections)
        self.disconnectWidget(self.ui.sections_listwidget)
        self.ui.sections_listwidget.itemClicked.connect(lambda: self.sectionsEntryClicked(self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.currentItem())))
        self.prev_section_list_item_widget = None
        if len(self.textbook_exercises) > 0:
            for i in range(self.ui.sections_listwidget.count()):
                chap_num = self.textbook_sections[i]["ChapterNumber"]
                sect_num = self.textbook_sections[i]["SectionNumber"]
                exercises = [entry for entry in self.textbook_exercises if entry["ChapterNumber"] == chap_num and entry["SectionNumber"] == sect_num]
                if len(exercises) > 0:
                    num = int(exercises[0]["ExerciseID"].split(".")[-1])
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-3].clicked.connect(
                        lambda state, num=num, exercises=exercises: self.exercise_page.showPage(num, exercises))
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-1].clicked.connect(
                        lambda state, exercises_to_be_added=exercises: self.add_to_study_list_page.showPage(exercises_to_be_added))
                    self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[1].stateChanged.connect(
                        lambda state, i=i: self.multipleSectionsSelected(self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i))))
            self.addButtonsToSectionActionButtonsLayout()
