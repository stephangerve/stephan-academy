import ElementStyles
from ContentPages.ClassPage import Page
from UIElements import ButtonElement
from UIElements import ListElement
from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont, QPixmap
import io
import os


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
    selected_exercises_stats = None
    selected_textbook_ID = None
    selected_category = None
    selected_author = None
    selected_textbook_title = None
    selected_edition = None
    selected_chap_num = None
    selected_sect_num = None


    def __init__(self, ui, ):
        Page.__init__(self, "Learning Page", 2)
        self.ui = ui
        self.initUI()



    def initUI(self):
        self.background_colors = {
            "A": "rgb(147, 235, 52)",
            "B": "rgb(217, 235, 52)",
            "C": "rgb(235, 171, 52)",
            "D": "rgb(235, 92, 52)",
            "F": "rgb(235, 52, 52)",
        }
        #self.query_table_names = ["Textbooks", "Sections", "Exercises"]
        #self.table_index = 0
        self.textbooks_list_element = ListElement(self.ui.textbooks_listwidget)
        self.sections_list_element = ListElement(self.ui.sections_listwidget)
        self.prev_selected_exercise_num = None
        self.prev_selected_exercise_bgcolor = None

    def objectReferences(self, db_interface, exercise_page, category_page, add_textbook_page):
        self.exercise_page = exercise_page
        self.db_interface = db_interface
        self.category_page = category_page
        self.add_textbook_page = add_textbook_page
        #self.connectButtons()
        #self.currently_selected = -1

    def showPage(self, cat_str):
        self.clearPage()
        self.selected_category = cat_str
        self.category_textbooks = self.db_interface.fetchEntries("Textbooks", [self.selected_category])
        self.textbooks_list_element.setList("Textbooks", self.category_textbooks)
        self.ui.textbooks_listwidget.itemClicked.connect(lambda: self.textbookEntryClicked(int(self.ui.textbooks_listwidget.currentItem().text())))
        self.ui.back_button.clicked.connect(lambda: self.category_page.showPage())
        self.ui.add_new_textbook_button.clicked.connect(lambda: self.add_textbook_page.showPage(cat_str))
        self.ui.content_pages.setCurrentIndex(self.page_number)

    def clearPage(self):
        self.clearExercisesGrid()
        self.ui.category_info_label.clear()
        self.ui.author_info_label.clear()
        self.ui.textbook_info_label.clear()
        self.ui.edition_info_label.clear()
        self.ui.chapter_info_label.clear()
        self.ui.section_info_label.clear()
        self.ui.ex_stats_info_grade_label.clear()
        self.ui.ex_stats_info_lastattempt_label.clear()
        self.ui.ex_stats_info_totalattempts_label.clear()
        self.ui.ex_stats_info_averagetime_label.clear()
        self.textbooks_list_element.clear()
        self.sections_list_element.clear()




    def textbookEntryClicked(self, ui_list_index):
        self.sections_list_element.clear()
        self.ui.chapter_info_label.clear()
        self.ui.section_info_label.clear()
        self.clearExercisesGrid()
        self.selected_textbook_ID = self.category_textbooks[ui_list_index - 1]["ID"]
        self.textbook_sections = self.db_interface.fetchEntries("Sections", [self.selected_textbook_ID])
        self.selected_author = self.category_textbooks[ui_list_index - 1]["Authors"]
        self.selected_textbook_title = self.category_textbooks[ui_list_index - 1]["Title"]
        self.selected_edition = self.category_textbooks[ui_list_index - 1]["Edition"]
        self.ui.category_info_label.setText(str(self.selected_category))
        self.ui.author_info_label.setText(str(self.selected_author))
        self.ui.textbook_info_label.setText(str(self.selected_textbook_title))
        self.ui.edition_info_label.setText(str(self.selected_edition))
        self.sections_list_element.setList("Sections", self.textbook_sections)
        self.ui.sections_listwidget.itemClicked.connect(lambda: self.sectionsEntryClicked(int(self.ui.sections_listwidget.currentItem().text())))


    def sectionsEntryClicked(self, ui_list_index):
        self.selected_chap_num = self.textbook_sections[ui_list_index - 1]["ID"]
        self.selected_sect_num = self.textbook_sections[ui_list_index - 1]["SectionNumber"]
        self.selected_exercises = self.db_interface.fetchEntries("Exercises", [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num])
        self.selected_exercises_stats = self.db_interface.fetchEntries("ExerciseStats", [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num])
        self.setExercisesButtons(self.selected_exercises, self.selected_exercises_stats)



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

    def setExercisesButtons(self, exercises, exercise_stats):
        self.clearExercisesGrid()
        self.ui.chapter_info_label.setText(str(self.selected_chap_num))
        self.ui.section_info_label.setText(str(self.selected_sect_num))
        count = len(exercises)
        if count > 0:
            exercise_stats_ids = [entry["ExerciseID"] for entry in exercise_stats]
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
                    ex_num = int(exercises[index]["ExerciseID"].split(".")[-1])
                    self.button = QPushButton(str(ex_num))
                    self.button.setCheckable(True)
                    if self.db_interface.fetchBool("SolutionExist", [exercises[index]["ID"], exercises[index]["ExerciseID"]]) is True:
                        if exercises[index]["ExerciseID"] in exercise_stats_ids:
                            grade = [entry["Grade"] for entry in exercise_stats if exercises[index]["ExerciseID"] == entry["ExerciseID"]][0]
                            if grade in self.background_colors.keys():
                                color = self.background_colors[grade]
                            else:
                                color = "gray"
                        else:
                            color = "white"
                        self.button.clicked.connect(lambda state, exnum=int(self.button.text()): self.showExerciseStats(exnum))
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
        if self.prev_selected_exercise_num is not None:
            self.ui.exercises_grid.itemAt(self.prev_selected_exercise_num - 1).widget().setEnabled(True)
            self.ui.exercises_grid.itemAt(self.prev_selected_exercise_num - 1).widget().toggle()
            self.ui.exercises_grid.itemAt(self.prev_selected_exercise_num - 1).widget().setStyleSheet("background-color : " + self.prev_selected_exercise_bgcolor)
        self.ui.exercises_grid.itemAt(num - 1).widget().setEnabled(False)
        self.ui.exercises_grid.itemAt(num - 1).widget().setStyleSheet("background-color : lightblue")
        self.prev_selected_exercise_num = num
        matched_entries = [entry for entry in self.selected_exercises_stats if int(entry["ExerciseID"].split(".")[-1]) == num]
        if len(matched_entries) > 0:
            exercise_stats = matched_entries[0]
            if exercise_stats["Attempts"] > 0:
                self.ui.ex_stats_info_grade_label.setText(str(exercise_stats["Grade"]))
                self.ui.ex_stats_info_lastattempt_label.setText(str(exercise_stats["LastAttempted"]))
                self.ui.ex_stats_info_totalattempts_label.setText(str(exercise_stats["Attempts"]))
                self.ui.ex_stats_info_averagetime_label.setText(str(exercise_stats["AverageTime"]))
                self.prev_selected_exercise_bgcolor = self.background_colors[exercise_stats["Grade"]]
            else:
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
        self.ui.start_button.clicked.connect(lambda state, num=num, exercises=self.selected_exercises, exercises_stats=self.selected_exercises_stats: self.exercise_page.showPage(num, exercises, exercises_stats))

