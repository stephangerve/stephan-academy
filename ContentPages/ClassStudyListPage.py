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
import matplotlib.pyplot as plt
import io
import numpy as np


class StudyListPage(Page):

    def __init__(self, ui, ):
        Page.__init__(self, Config.StudyListPage_page_number)
        self.ui = ui
        self.sl_list_element = ListElement(self.ui.study_lists_listwidget)
        self.sl_chap_sects_list_element = ListElement(self.ui.sl_sections_listwidget)
        self.sect_grades_counts = {}


    def objectReferences(self, db_interface, exercise_page, study_lists):
        self.db_interface = db_interface
        self.exercise_page = exercise_page
        self.study_lists = study_lists


    def showPage(self):
        self.prev_study_list_widget_item = None
        self.prev_section_list_widget_item = None
        if self.ui.study_lists_listwidget.count() > 0:
            self.ui.study_lists_listwidget.itemClicked.disconnect()
        if self.ui.sl_sections_listwidget.count() > 0:
            self.ui.sl_sections_listwidget.itemClicked.disconnect()
        self.ui.progress_donut_label.clear()
        self.ui.sb_frame_2.setStyleSheet("background-color: gray")
        self.ui.start_button_2.setStyleSheet("color: black")
        self.ui.start_button_2.setEnabled(False)
        # ElementStyles.regularShadow(self.ui.progress_donut_label)
        # self.ui.progress_donut_frame.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.ui.progress_donut_frame.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.ui.progress_donut_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.ui.progress_donut_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.ui.remove_from_sl_button)
        ElementStyles.regularShadow(self.ui.textbook_info_frame_left_2)
        ElementStyles.regularShadow(self.ui.ex_stats_info_2)
        ElementStyles.regularShadow(self.ui.sb_frame_2)
        ElementStyles.lightShadow(self.ui.start_button_2)
        ElementStyles.lightShadow(self.ui.mode_frame_2)
        ElementStyles.lightShadow(self.ui.grade_filter_frame_2)
        self.ui.button_studylist.setChecked(True)
        self.ui.button_studylist.setEnabled(False)
        self.ui.button_studylist.setStyleSheet("background-color: rgb(58, 74, 97); color: white")
        self.ui.button_studylist.setCursor(QCursor(QtCore.Qt.ArrowCursor))
        pushbuttons = [self.ui.button_dashboard, self.ui.button_flashcards, self.ui.button_learn]
        for button in pushbuttons:
            if button.isChecked():
                button.setChecked(False)
                button.setEnabled(True)
                button.setStyleSheet("background-color: #2A4D87; color: white")
                button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        # self.ui.sl_sections_listwidget.blockSignals(True)
        # self.ui.study_lists_listwidget.blockSignals(True)
        # self.ui.add_new_exercises_button.clicked.connect(lambda: None)
        # self.ui.back_button.clicked.connect(lambda: None)
        # self.ui.start_button_2.clicked.connect(lambda: None)
        # self.ui.add_to_a_study_list_button.clicked.connect(lambda: None)
        # self.ui.remove_from_a_study_list_button.clicked.connect(lambda: None)
        self.clearExercisesGrid()
        self.sl_list_element.clear()
        self.sl_chap_sects_list_element.clear()
        self.all_sl_exercises = self.db_interface.fetchEntries("All Study List Exercises", [])
        self.all_sl_exercises_dict = dict(zip([entry["StudyListID"] for entry in self.study_lists], [{} for i in range(len(self.study_lists))]))
        for ex in self.all_sl_exercises:
            tags = ex["Tags"].split(",")
            for tag in tags:
                if ex["TextbookID"] not in self.all_sl_exercises_dict[tag].keys():
                    self.all_sl_exercises_dict[tag][ex["TextbookID"]] = {}
                chap_sect_num = ".".join([ex["ChapterNumber"], ex["SectionNumber"]])
                if chap_sect_num not in self.all_sl_exercises_dict[tag][ex["TextbookID"]].keys():
                    self.all_sl_exercises_dict[tag][ex["TextbookID"]][chap_sect_num] = []
                self.all_sl_exercises_dict[tag][ex["TextbookID"]][chap_sect_num].append(ex)
        self.sl_list_element.setList("Study List", self.study_lists)
        self.ui.study_lists_listwidget.itemClicked.connect(lambda: self.studyListClicked(self.ui.study_lists_listwidget.currentItem()))
        # self.ui.study_lists_listwidget.blockSignals(False)
        self.selected_chap_sect = None
        self.ui.content_pages.setCurrentIndex(self.page_number)

    def showProgressDonut(self):
        grades_dict = dict(zip(['A','B','C','D','F','NG'], [0]*6))

        for txtbk in self.all_sl_exercises_dict[self.selected_tag]:
            for chap_sect_num in self.all_sl_exercises_dict[self.selected_tag][txtbk]:
                for exercise in self.all_sl_exercises_dict[self.selected_tag][txtbk][chap_sect_num]:
                    if exercise["Grade"] in list(grades_dict.keys()):
                        grades_dict[exercise["Grade"]] += 1
                    else:
                        grades_dict["NG"] += 1
        plt.figure().clear()
        plt.pie(list(grades_dict.values()), colors=[tuple([val / 255 for val in color]) for color in list(Config.EXERCISE_GRADE_COLORS.values()) + [Config.GREY_LIGHT_BLUE]], radius=0.8)
        centre_circle = plt.Circle((0, 0), 0.6, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        buffer = io.BytesIO()
        fig.savefig(buffer, format='raw')
        plt.close(fig)
        buffer.seek(0)
        img_arr = np.reshape(np.frombuffer(buffer.getvalue(), dtype=np.uint8), newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
        buffer.close()
        height, width, channel = img_arr.shape
        bytesPerLine = channel * width
        qImg = QImage(img_arr, width, height, bytesPerLine, QImage.Format_RGBX8888)
        image_pixmap = QPixmap(qImg)
        self.ui.progress_donut_label.setPixmap(image_pixmap)


    def studyListClicked(self, listwidgetitem):
        self.ui.sb_frame.setStyleSheet("background-color: gray")
        self.ui.start_button_2.setStyleSheet("color: black")
        self.ui.start_button_2.setEnabled(False)
        self.sl_chap_sects_list_element.clear()
        self.ui.chapter_info_label.clear()
        self.ui.section_info_label.clear()
        self.clearExercisesGrid()
        self.selected_tag = [entry["StudyListID"] for entry in self.study_lists if self.study_lists[int(listwidgetitem.text()) - 1]["StudyListName"] == entry["StudyListName"]][0]
        self.selected_sl_chap_sects = [[txtbk, chap_sect.split(".")[0], chap_sect.split(".")[1], {}] for txtbk in self.all_sl_exercises_dict[self.selected_tag] for chap_sect in self.all_sl_exercises_dict[self.selected_tag][txtbk].keys()]
        self.updateSLSectionList()
        self.showProgressDonut()
        self.ui.sl_sections_listwidget.itemClicked.connect(lambda: self.studyListSectionClicked(self.ui.sl_sections_listwidget.currentItem()))
        for i in range(self.ui.sl_sections_listwidget.count()):
            chap_sect_num = ".".join([self.selected_sl_chap_sects[i][1], self.selected_sl_chap_sects[i][2]])
            exercises = self.all_sl_exercises_dict[self.selected_tag][self.selected_sl_chap_sects[i][0]][chap_sect_num]
            if len(exercises) > 0:
                num = int(exercises[0]["ExerciseID"].split(".")[-1])
                self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i)).children()[-1].clicked.connect(lambda state, num=num, exercises=exercises: self.exercise_page.showPage(num, exercises))
        ElementStyles.selectedListItem(self.ui.study_lists_listwidget.itemWidget(listwidgetitem))
        if self.prev_study_list_widget_item is not None:
            ElementStyles.unselectedListItem(self.prev_study_list_widget_item)
        self.prev_study_list_widget_item = self.ui.study_lists_listwidget.itemWidget(listwidgetitem)
        self.prev_section_list_widget_item = None

    def studyListSectionClicked(self, listwidgetitem):
        self.ui.sb_frame.setStyleSheet("background-color: gray")
        self.ui.start_button_2.setStyleSheet("color: black")
        self.ui.start_button_2.setEnabled(False)
        self.selected_chap_sect = self.selected_sl_chap_sects[int(listwidgetitem.text()) - 1]
        self.selected_exercises = self.all_sl_exercises_dict[self.selected_tag][self.selected_chap_sect[0]][".".join(self.selected_chap_sect[1:3])]
        self.setExercisesButtons()
        textbook_info = self.db_interface.fetchEntries("Textbook Info", [self.selected_exercises[0]["TextbookID"]])[0]
        self.ui.category_info_label_2.setText(str(textbook_info["Category"]))
        self.ui.textbook_info_label_2.setText(" - ".join([textbook_info["Authors"], textbook_info["Title"], textbook_info["Edition"]]))
        ElementStyles.selectedListItem(self.ui.sl_sections_listwidget.itemWidget(listwidgetitem))
        if self.prev_section_list_widget_item is not None:
            ElementStyles.unselectedListItem(self.prev_section_list_widget_item)
        self.prev_section_list_widget_item = self.ui.sl_sections_listwidget.itemWidget(listwidgetitem)


    def updateSLSectionList(self):
        for sect_entry in self.selected_sl_chap_sects:
            sect_entry[3]["NumExercisesA"] = sum([1 for entry in self.all_sl_exercises if entry["ChapterNumber"] == sect_entry[1] and entry["SectionNumber"] == sect_entry[2] and entry["Grade"] == 'A'])
            sect_entry[3]["NumExercisesB"] = sum([1 for entry in self.all_sl_exercises if entry["ChapterNumber"] == sect_entry[1] and entry["SectionNumber"] == sect_entry[2] and entry["Grade"] == 'B'])
            sect_entry[3]["NumExercisesC"] = sum([1 for entry in self.all_sl_exercises if entry["ChapterNumber"] == sect_entry[1] and entry["SectionNumber"] == sect_entry[2] and entry["Grade"] == 'C'])
            sect_entry[3]["NumExercisesD"] = sum([1 for entry in self.all_sl_exercises if entry["ChapterNumber"] == sect_entry[1] and entry["SectionNumber"] == sect_entry[2] and entry["Grade"] == 'D'])
            sect_entry[3]["NumExercisesF"] = sum([1 for entry in self.all_sl_exercises if entry["ChapterNumber"] == sect_entry[1] and entry["SectionNumber"] == sect_entry[2] and entry["Grade"] == 'F'])
            sect_entry[3]["NoGrade"] = sum([1 for entry in self.all_sl_exercises if entry["ChapterNumber"] == sect_entry[1] and entry["SectionNumber"] == sect_entry[2] and entry["SolutionExists"] == 'True' and entry["Attempts"] == 0])
        self.sl_chap_sects_list_element.setList("Selected Study List Sections", self.selected_sl_chap_sects)

    def clearExercisesGrid(self):
        for i in reversed(range(self.ui.sl_exercises_grid.count())):
            self.ui.sl_exercises_grid.itemAt(i).widget().setParent(None)


    def setExercisesButtons(self):
        self.prev_selected_exercise_num = None
        self.clearExercisesGrid()
        self.ui.chapter_info_label_2.setText(str(self.selected_chap_sect[1]))
        self.ui.section_info_label_2.setText(str(self.selected_chap_sect[2]))
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
                    self.ui.sl_exercises_grid.addWidget(self.button, i, j)
        else:
            label = QLabel("\n\n\n\n\nNo Exercises!")
            color = "white"
            label.setStyleSheet("background-color : " + color)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFont(QFont("Arial", 12))
            label.resize(60, 80)
            self.ui.sl_exercises_grid.addWidget(label, 0, 0)

    def showExerciseStats(self, num):
        self.ui.sb_frame_2.setStyleSheet("background-color: rgb(0, 170, 127)")
        self.ui.start_button_2.setStyleSheet("color: white")
        self.ui.start_button_2.setEnabled(True)
        if self.prev_selected_exercise_num is not None:
            last_grid_index = [self.selected_exercises.index(entry) for entry in self.selected_exercises if int(entry["ExerciseID"].split(".")[-1]) == self.prev_selected_exercise_num][0]
            self.ui.sl_exercises_grid.itemAt(last_grid_index).widget().setEnabled(True)
            self.ui.sl_exercises_grid.itemAt(last_grid_index).widget().toggle()
            self.ui.sl_exercises_grid.itemAt(last_grid_index).widget().setStyleSheet("background-color : " + self.prev_selected_exercise_bgcolor)
        grid_index, exercise_stats = [[self.selected_exercises.index(entry), entry] for entry in self.selected_exercises if int(entry["ExerciseID"].split(".")[-1]) == num][0]
        self.prev_selected_exercise_num = num
        self.ui.sl_exercises_grid.itemAt(grid_index).widget().setEnabled(False)
        self.ui.sl_exercises_grid.itemAt(grid_index).widget().setStyleSheet("background-color : lightblue")
        if eval(exercise_stats["Seen"]) and exercise_stats["Attempts"] > 0:
            self.ui.ex_stats_info_grade_label_2.setText(str(exercise_stats["Grade"]))
            self.ui.ex_stats_info_lastattempt_label_2.setText(str(exercise_stats["LastAttempted"]) + " -- " + str(exercise_stats["LastAttemptTime"]))
            self.ui.ex_stats_info_totalattempts_label_2.setText(str(exercise_stats["Attempts"]))
            self.ui.ex_stats_info_averagetime_label_2.setText(str(exercise_stats["AverageTime"]))
            self.prev_selected_exercise_bgcolor = "rgb" + str(Config.EXERCISE_GRADE_COLORS[exercise_stats["Grade"]])
        elif eval(exercise_stats["Seen"]) and exercise_stats["Attempts"] == 0:
            self.ui.ex_stats_info_grade_label_2.setText("N/A")
            self.ui.ex_stats_info_lastattempt_label_2.setText("N/A")
            self.ui.ex_stats_info_totalattempts_label_2.setText("N/A")
            self.ui.ex_stats_info_averagetime_label_2.setText("N/A")
            self.prev_selected_exercise_bgcolor = "gray"
        else:
            self.ui.ex_stats_info_grade_label_2.setText("N/A")
            self.ui.ex_stats_info_lastattempt_label_2.setText("N/A")
            self.ui.ex_stats_info_totalattempts_label_2.setText("N/A")
            self.ui.ex_stats_info_averagetime_label_2.setText("N/A")
            self.prev_selected_exercise_bgcolor = "white"
        for i in reversed(range(self.ui.ex_study_list_tablewidget.rowCount())):
            self.ui.ex_study_list_tablewidget.removeRow(i)
        self.ui.start_button_2.clicked.connect(lambda state, num=num, exercises=self.selected_exercises: self.exercise_page.showPage(num, exercises))

