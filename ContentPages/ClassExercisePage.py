import ElementStyles
from ContentPages.ClassPage import Page
from ClassDBInterface import DBInterface
from UIElements import ButtonElement
from UIElements import ListElement
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QSound, QSoundEffect
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import pyqtSlot, QUrl
from multiprocessing import Process
import io
import os
import time
import datetime
from datetime import date, timedelta

drive_letter = "C:"
main_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\"
learning_system_dir = os.path.join(main_dir, "Learning System")
e_packs_dir = os.path.join(main_dir, "Exercise Packs")
sound_warning_path = os.path.join(learning_system_dir, "sounds", "warning - Universfield from Pixabay.wav")
sound_tick_path = os.path.join(learning_system_dir, "sounds", "tick edited 2 - Universfield from Pixabay.wav")
sound_next_path = os.path.join(learning_system_dir, "sounds", "next edited 2 - Universfield from Pixabay.wav")

class ExercisePage(Page):
    ui = None
    exercises = None
    exercise_stats = None
    current_exercise = None
    current_exercise_number = None
    MAX_TIME = 480 #420
    WARNING_TIME = 120



    def __init__(self, ui):
        Page.__init__(self, "Exercices Page", 3)
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
        self.ui.next_exercise_button.clicked.connect(lambda state, grade=None: self.processGrade(grade, "Next"))
        self.ui.prev_exercise_button.clicked.connect(lambda state, grade=None: self.processGrade(grade, "Prev"))
        self.sound_warning = QSoundEffect()
        self.sound_tick = QSoundEffect()
        self.sound_next = QSoundEffect()
        self.sound_warning.setSource(QUrl.fromLocalFile(sound_warning_path))
        self.sound_tick.setSource(QUrl.fromLocalFile(sound_tick_path))
        self.sound_next.setSource(QUrl.fromLocalFile(sound_next_path))
        self.hide_timer = QTimer()
        self.start_hide_timer = QTimer()
        self.exercise_timer = QTimer()
        self.timer_counter = None

    def objectReferences(self, db_interface, learning_page):
        self.db_interface = db_interface
        self.learning_page = learning_page

    def showPage(self, num, exercises, exercise_stats):
        self.current_exercise_number = num
        self.exercises = exercises
        #self.exercise_stats = self.db_interface.fetchEntries("ExerciseStats", [self.exercises[0]["ID"], self.exercises[0]["ChapterNumber"], self.exercises[0]["SectionNumber"]])
        self.exercise_stats = exercise_stats
        self.exercises_stats_columns = self.db_interface.fetchColumnNames("ExerciseStats", [self.exercises[0]["ID"], self.exercises[0]["ChapterNumber"], self.exercises[0]["SectionNumber"]])
        self.ui.exit_practice_button.clicked.connect(lambda: self.exitPractice())
        self.ui.content_pages.setCurrentIndex(self.page_number)
        self.startExercise()

    def exitPractice(self):
        try:
            if self.exercise_timer.isActive():
                self.exercise_timer.disconnect()
        except:
            pass
        try:
            if self.start_hide_timer.isActive():
                self.start_hide_timer.disconnect()
        except:
            pass
        try:
            if self.hide_timer.isActive():
                self.hide_timer.disconnect()
        except:
            pass
        self.learning_page.selected_exercises_stats = self.exercise_stats
        self.learning_page.setExercisesButtons(self.exercises, self.learning_page.selected_exercises_stats)
        self.learning_page.prev_selected_exercise_num = None
        self.learning_page.prev_selected_exercise_bgcolor = None
        self.ui.content_pages.setCurrentIndex(self.learning_page.page_number)

    def showNotification(self, notif_str):
        try:
            if self.start_hide_timer.isActive():
                self.start_hide_timer.disconnect()
            if self.hide_timer.isActive():
                self.hide_timer.disconnect()
        except:
            pass
        for i in reversed(range(self.ui.popup_note_layout.count())):
            self.ui.popup_note_layout.itemAt(i).widget().setParent(None)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.popup_label = QLabel(notif_str)
        self.popup_label.setAlignment(QtCore.Qt.AlignCenter)
        #self.popup_label.resize(60, 30)
        self.popup_label.setStyleSheet("background-color: #2A4D87;"
                                       "color: white;"
                                       "border: 5px solid;"
                                       "border-color: rgb(58, 74, 97);")
        self.op_level = 0.8
        self.opacity_effect.setOpacity(self.op_level)
        self.popup_label.setGraphicsEffect(self.opacity_effect)
        self.ui.popup_note_layout.addWidget(self.popup_label)
        self.start_hide_timer.singleShot(3000, self.hideNotification)

    def hideNotification(self):
        self.hide_timer.start(100)
        self.hide_timer.timeout.connect(lambda: self.fadeLabel(self.popup_label))


    def fadeLabel(self, label):
        self.op_level = self.op_level - 0.05
        if self.op_level <= 0.0:
            self.opacity_effect.setOpacity(0.0)
            label.setGraphicsEffect(self.opacity_effect)
            self.hide_timer.disconnect()
        else:
            self.opacity_effect.setOpacity(self.op_level)
            label.setGraphicsEffect(self.opacity_effect)

    def updateTimerTicker(self):
        self.timer_counter = self.timer_counter - 1
        self.ui.timer_ticker.setText(str((datetime.datetime(1, 1, 1, 0, 0) + timedelta(seconds=self.timer_counter)).strftime("%M:%S")))
        if self.timer_counter == self.WARNING_TIME:
            self.sound_warning.play()
            self.showNotification("Two Minutes Left!")
        if self.timer_counter <= self.WARNING_TIME:
            self.ui.timer_ticker.setStyleSheet("color: red")
        if 0 < self.timer_counter < 10:
            self.sound_tick.play()
        if self.timer_counter == 0:
            self.exercise_timer.disconnect()
            self.processGrade(None, "Next")


    def startExercise(self):
        self.sound_next.play()
        try:
            if self.exercise_timer.isActive():
                self.exercise_timer.disconnect()
        except:
            pass
        self.ui.timer_ticker.setText(str((datetime.datetime(1, 1, 1, 0, 0) + timedelta(seconds=self.MAX_TIME)).strftime("%M:%S")))
        self.ui.problem_pic_label.clear()
        self.ui.solution_pic_label.clear()
        for i in reversed(range(self.ui.grade_hboxlayout.count())):
            self.ui.grade_hboxlayout.itemAt(i).widget().setParent(None)
        self.current_exercise = [entry for entry in self.exercises if int(entry["ExerciseID"].split(".")[-1]) == self.current_exercise_number][0]
        exercise_path = os.path.join(e_packs_dir, "\\".join(self.current_exercise["UnmaskedExercisePath"].split(" -- ")))
        problem_pic_label = QPixmap(exercise_path)
        self.ui.problem_pic_label.setPixmap(problem_pic_label)
        self.ui.problem_pic_label.resize(problem_pic_label.width(), problem_pic_label.height())
        button = QPushButton("Finish")
        button.resize(50, 50)
        button.clicked.connect(lambda state: self.finishedExercise())
        self.ui.grade_hboxlayout.addWidget(button)
        self.setExercisesButtons()
        self.timer_counter = self.MAX_TIME
        self.exercise_timer.start(1000)
        self.exercise_timer.timeout.connect(lambda: self.updateTimerTicker())

    def finishedExercise(self):
        self.exercise_timer.disconnect()
        solution_path = os.path.join(e_packs_dir, "\\".join(self.current_exercise["SolutionPath"].split(" -- ")))
        solution_image_pixmap = QPixmap(solution_path)
        self.ui.solution_pic_label.setPixmap(solution_image_pixmap)
        self.ui.solution_pic_label.resize(solution_image_pixmap.width(), solution_image_pixmap.height())
        self.ui.grade_hboxlayout.itemAt(0).widget().setParent(None)
        for grade in self.background_colors.keys():
            button = QPushButton(grade)
            button.setStyleSheet("background-color : " + self.background_colors[grade])
            button.clicked.connect(lambda state, grade=button.text(): self.processGrade(grade, "Next"))
            self.ui.grade_hboxlayout.addWidget(button)


    def processGrade(self, grade, direction, desired_next_num=None):
        current_exercise_stat = []
        matched_entries = [self.exercise_stats.pop(self.exercise_stats.index(entry)) for entry in self.exercise_stats if self.current_exercise["ExerciseID"] == entry["ExerciseID"]]
        if len(matched_entries) > 0:
            current_exercise_stat = matched_entries[0]
        if len(current_exercise_stat) == 0:
            current_exercise_stat = dict(
                zip(self.exercises_stats_columns,
                    [
                        self.current_exercise["ID"],
                        self.current_exercise["ExerciseID"],
                        0,
                        None,
                        None,
                        None,
                        None,
                        None,
                    ]
                )
            )
        if grade is not None:
            current_exercise_stat["Attempts"] += 1
            current_exercise_stat["LastAttempted"] = date.today().strftime("%m/%d/%Y")
            current_exercise_stat["LastAttemptTime"] = datetime.datetime.now().strftime("%H:%M")
            current_exercise_stat["Grade"] = grade
            old_avg_time = 0
            if int(current_exercise_stat["Attempts"]) - 1 >= 1:
                if current_exercise_stat["AverageTime"] is not None:
                    old_avg_time = float(current_exercise_stat["AverageTime"])
                else:
                    old_avg_time = 0
            current_exercise_stat["AverageTime"] = (((self.MAX_TIME - self.timer_counter)/60) + old_avg_time * (int(current_exercise_stat["Attempts"]) - 1)) / int(current_exercise_stat["Attempts"]) #derivation of formula in notepad on desk
        self.exercise_stats.append(current_exercise_stat)
        self.showNotification("Attempt saved")
        if direction == "Next":
            self.current_exercise_number = self.current_exercise_number + 1
            while self.current_exercise_number <= int(self.exercises[-1]["ExerciseID"].split(".")[-1]):
                self.current_exercise = [entry for entry in self.exercises if int(entry["ExerciseID"].split(".")[-1]) == self.current_exercise_number][0]
                if self.current_exercise["SolutionExists"] is not None and eval(self.current_exercise["SolutionExists"]) == True:
                    break
                else:
                    self.current_exercise_number = self.current_exercise_number + 1
                    if self.current_exercise_number > int(self.exercises[-1]["ExerciseID"].split(".")[-1]):
                        self.ui.content_pages.setCurrentIndex(self.learning_page.page_number)
            if self.current_exercise_number > int(self.exercises[-1]["ExerciseID"].split(".")[-1]):
                self.ui.content_pages.setCurrentIndex(self.learning_page.page_number)
            else:
                self.startExercise()
        elif direction == "Prev":
            self.current_exercise_number = self.current_exercise_number - 1
            while self.current_exercise_number >= int(self.exercises[0]["ExerciseID"].split(".")[-1]):
                self.current_exercise = [entry for entry in self.exercises if int(entry["ExerciseID"].split(".")[-1]) == self.current_exercise_number][0]
                if self.current_exercise["SolutionExists"] is not None and eval(self.current_exercise["SolutionExists"]) == True:
                    break
                else:
                    self.current_exercise_number = self.current_exercise_number - 1
                    if self.current_exercise_number < int(self.exercises[0]["ExerciseID"].split(".")[-1]):
                        self.ui.content_pages.setCurrentIndex(self.learning_page.page_number)
            if self.current_exercise_number < int(self.exercises[0]["ExerciseID"].split(".")[-1]):
                self.ui.content_pages.setCurrentIndex(self.learning_page.page_number)
            else:
                self.startExercise()
        elif direction == "Cond3":
            self.current_exercise_number = desired_next_num
            self.startExercise()





    def clearExercisesGrid(self):
        for i in reversed(range(self.ui.exercise_page_exercises_grid.count())):
            self.ui.exercise_page_exercises_grid.itemAt(i).widget().setParent(None)

    def setExercisesButtons(self):
        self.clearExercisesGrid()
        count = len(self.exercises)
        if count > 0:
            exercise_stats_ids = [entry["ExerciseID"] for entry in self.exercise_stats]
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
                    ex_num = int(self.exercises[index]["ExerciseID"].split(".")[-1])
                    button = QPushButton(str(ex_num))
                    button.setCheckable(True)
                    if self.db_interface.fetchBool("SolutionExist", [self.exercises[index]["ID"], self.exercises[index]["ExerciseID"]]) is True:
                        if self.exercises[index]["ExerciseID"] == self.current_exercise["ExerciseID"]:
                            color = "lightblue"
                            button.toggle()
                            button.setEnabled(False)
                        elif self.exercises[index]["ExerciseID"] in exercise_stats_ids:
                            grade = [entry["Grade"] for entry in self.exercise_stats if self.exercises[index]["ExerciseID"] == entry["ExerciseID"]][0]
                            if grade in self.background_colors.keys():
                                color = self.background_colors[grade]
                            else:
                                color = "gray"
                        else:
                            color = "white"
                        button.clicked.connect(lambda state, next_num=int(button.text()): self.processGrade(None, "Cond3", desired_next_num=next_num))
                    else:
                        color = "lightgray"
                        button.toggle()
                        button.setEnabled(False)
                    button.setStyleSheet("background-color : " + color)
                    self.ui.exercise_page_exercises_grid.addWidget(button, i, j)
        else:
            label = QLabel("\n\n\n\n\nNo Exercises!")
            color = "white"
            label.setStyleSheet("background-color : " + color)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFont(QFont("Arial", 12))
            label.resize(60, 30)
            self.ui.exercise_page_exercises_grid.addWidget(label, 0, 0)


