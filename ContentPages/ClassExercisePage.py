import ElementStyles
from ContentPages.ClassPage import Page
from ClassDBInterface import DBInterface
from CustomWidgets.ClassListWidget import ListWidget
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QSound, QSoundEffect
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QFont, QPixmap, QCursor
from PyQt5.QtCore import pyqtSlot, QUrl
from multiprocessing import Process
import io
import os
import time
import Config
from datetime import date, timedelta, datetime


class ExercisePage(Page):
    ui = None
    exercises = None
    current_exercise = None
    current_exercise_number = None
    MAX_TIME = 480 #420
    WARNING_TIME = 120



    def __init__(self, ui):
        Page.__init__(self, Config.ExercisePage_page_number)
        self.ui = ui
        self.initUI()


    def initUI(self):
        self.ui.next_exercise_button.clicked.connect(lambda state, grade=None: self.processGrade(grade, "Next"))
        self.ui.prev_exercise_button.clicked.connect(lambda state, grade=None: self.processGrade(grade, "Prev"))
        self.sound_warning = QSoundEffect()
        self.sound_tick = QSoundEffect()
        self.sound_next = QSoundEffect()
        self.sound_warning.setSource(QUrl.fromLocalFile(Config.SOUND_WARNING))
        self.sound_tick.setSource(QUrl.fromLocalFile(Config.SOUND_TICK))
        self.sound_next.setSource(QUrl.fromLocalFile(Config.SOUND_NEXT))
        self.hide_timer = QTimer()
        self.start_hide_timer = QTimer()
        self.exercise_timer = QTimer()
        self.timer_counter = None

    def objectReferences(self, db_interface, learning_page, add_to_study_list_page, study_list_page):
        self.db_interface = db_interface
        self.learning_page = learning_page
        self.add_to_study_list_page = add_to_study_list_page
        self.study_list_page = study_list_page

    def showPage(self, num, exercises):
        self.current_exercise_number = num
        self.exercises = exercises
        self.clearNotificationLayout()
        self.ui.timer_ticker.setStyleSheet("color: white;\nfont: 12pt;")
        self.disconnectWidget(self.ui.exit_practice_button)
        self.ui.exit_practice_button.clicked.connect(lambda: self.exitPractice())
        self.last_page_number = self.ui.content_pages.currentIndex()
        if self.last_page_number == self.learning_page.page_number:
            self.date_filter = self.learning_page.date_filter
        elif self.last_page_number == self.study_list_page.page_number:
            self.date_filter = self.study_list_page.date_filter

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
        if self.last_page_number == self.learning_page.page_number:
            self.learning_page.selected_exercises = self.exercises
            self.learning_page.setExercisesButtons()
            self.learning_page.updateSectionList()
            for i in range(self.ui.sections_listwidget.count()):
                chap_num = self.learning_page.textbook_sections[i]["ChapterNumber"]
                sect_num = self.learning_page.textbook_sections[i]["SectionNumber"]
                exercises = [entry for entry in self.learning_page.textbook_exercises if entry["ChapterNumber"] == chap_num and entry["SectionNumber"] == sect_num]
                num = int(exercises[0]["ExerciseID"].split(".")[-1])
                self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-3].clicked.connect(lambda state, num=num, exercises=exercises: self.showPage(num, exercises))
                self.ui.sections_listwidget.itemWidget(self.ui.sections_listwidget.item(i)).children()[-1].clicked.connect(lambda state, exercises_to_be_added=exercises: self.add_to_study_list_page.showPage(exercises_to_be_added))
            self.learning_page.prev_selected_exercise_num = None
            self.learning_page.prev_selected_exercise_bgcolor = None
        elif self.last_page_number == self.study_list_page.page_number:
            self.study_list_page.selected_section["Exercises"] = self.exercises
            self.study_list_page.setExercisesButtons()
            self.study_list_page.updateGradeDistribution()
            self.study_list_page.updateSLSectionList()
            progress_label = self.study_list_page.prev_study_list_item_widget.children()[7]
            self.study_list_page.sl_chap_sects_list_element.updateProgressBar(progress_label, self.study_list_page.sl_collections_dict[self.study_list_page.selected_collection][self.study_list_page.selected_study_list])
            for i in range(self.ui.sl_sections_listwidget.count()):
                self.disconnectWidget(self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i)).children()[-2])
                self.disconnectWidget(self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i)).children()[1])
                self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i)).children()[-2].clicked.connect(lambda state, i=i: self.study_list_page.startButtonClicked(self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i))))
                self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i)).children()[1].stateChanged.connect(lambda state, i=i: self.study_list_page.multipleSectionsSelected(self.ui.sl_sections_listwidget.itemWidget(self.ui.sl_sections_listwidget.item(i))))
            self.study_list_page.prev_selected_exercise_num = None
            self.study_list_page.prev_selected_exercise_bgcolor = None
        self.ui.content_pages.setCurrentIndex(self.last_page_number)
        return

    def clearNotificationLayout(self):
        for i in reversed(range(self.ui.popup_note_layout.count())):
            self.ui.popup_note_layout.itemAt(i).widget().setParent(None)

    def showNotification(self, notif_str):
        try:
            if self.start_hide_timer.isActive():
                self.start_hide_timer.disconnect()
            if self.hide_timer.isActive():
                self.hide_timer.disconnect()
        except:
            pass
        self.clearNotificationLayout()
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
        self.ui.timer_ticker.setText(str((datetime(1, 1, 1, 0, 0) + timedelta(seconds=self.timer_counter)).strftime("%M:%S")))
        if self.timer_counter == self.WARNING_TIME:
            self.sound_warning.play()
            self.showNotification("Two Minutes Left!")
        if self.timer_counter <= self.WARNING_TIME:
            self.ui.timer_ticker.setStyleSheet("color: red;\nfont: 12pt;")
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
        self.ui.timer_ticker.setText(str((datetime(1, 1, 1, 0, 0) + timedelta(seconds=self.MAX_TIME)).strftime("%M:%S")))
        self.ui.timer_ticker.setStyleSheet("color: white;\nfont: 12pt;")
        self.ui.problem_pic_label.clear()
        self.ui.solution_pic_label.clear()
        for i in reversed(range(self.ui.grade_hboxlayout.count())):
            self.ui.grade_hboxlayout.itemAt(i).widget().setParent(None)
        self.current_exercise = [entry for entry in self.exercises if int(entry["ExerciseID"].split(".")[-1]) == self.current_exercise_number][0]
        exercise_path = os.path.join(Config.E_PACKS_DIR, "\\".join(self.current_exercise["UnmaskedExercisePath"].split(" -- ")))
        problem_pic_label = QPixmap(exercise_path)
        self.ui.problem_pic_label.setPixmap(problem_pic_label)
        self.ui.problem_pic_label.resize(problem_pic_label.width(), problem_pic_label.height())
        self.ui.problem_pic_scroll_area.verticalScrollBar().setValue(0)
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
        solution_path = os.path.join(Config.E_PACKS_DIR, "\\".join(self.current_exercise["SolutionPath"].split(" -- ")))
        solution_image_pixmap = QPixmap(solution_path)
        self.ui.solution_pic_label.setPixmap(solution_image_pixmap)
        self.ui.solution_pic_label.resize(solution_image_pixmap.width(), solution_image_pixmap.height())
        self.ui.grade_hboxlayout.itemAt(0).widget().setParent(None)
        for grade in Config.EXERCISE_GRADE_COLORS.keys():
            button = QPushButton(grade)
            button.setStyleSheet("background-color : rgb" + str(Config.EXERCISE_GRADE_COLORS[grade]))
            button.clicked.connect(lambda state, grade=button.text(): self.processGrade(grade, "Next"))
            self.ui.grade_hboxlayout.addWidget(button)


    def processGrade(self, grade, direction, desired_next_num=None):
        popped_index = [i for i in range(len(self.exercises)) if self.current_exercise["ExerciseID"] == self.exercises[i]["ExerciseID"]][0]
        exercise_being_processed = self.exercises.pop(popped_index)
        exercise_being_processed["Seen"] = 'True'
        if grade is not None:
            exercise_being_processed["Attempts"] += 1
            exercise_being_processed["LastAttempted"] = date.today().strftime("%m/%d/%Y")
            exercise_being_processed["LastAttemptTime"] = datetime.now().strftime("%H:%M")
            exercise_being_processed["Grade"] = grade
            old_avg_time = 0
            if int(exercise_being_processed["Attempts"]) - 1 >= 1:
                if exercise_being_processed["AverageTime"] is not None:
                    old_avg_time = float(exercise_being_processed["AverageTime"])
                else:
                    old_avg_time = 0
            exercise_being_processed["AverageTime"] = (((self.MAX_TIME - self.timer_counter)/60) + old_avg_time * (int(exercise_being_processed["Attempts"]) - 1)) / int(exercise_being_processed["Attempts"]) #derivation of formula in notepad on desk
        self.exercises.insert(popped_index, exercise_being_processed)
        if exercise_being_processed["AverageTime"] == '':
            exercise_being_processed["AverageTime"] = 0.0
        update_params = [exercise_being_processed["Seen"],
                         exercise_being_processed["Attempts"],
                         exercise_being_processed["LastAttempted"],
                         exercise_being_processed["LastAttemptTime"],
                         exercise_being_processed["Grade"],
                         exercise_being_processed["AverageTime"],
                         exercise_being_processed["TextbookID"],
                         exercise_being_processed["ExerciseID"]]
        self.db_interface.updateEntry("Exercise", update_params)
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
                        self.exitPractice()
            if self.current_exercise_number > int(self.exercises[-1]["ExerciseID"].split(".")[-1]):
                self.exitPractice()
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
                        self.exitPractice()
            if self.current_exercise_number < int(self.exercises[0]["ExerciseID"].split(".")[-1]):
                self.exitPractice()
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
                    button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                    button.setCheckable(True)
                    if self.exercises[index]["SolutionExists"] is not None:
                        if eval(self.exercises[index]["SolutionExists"]):
                            if self.exercises[index]["ExerciseID"] == self.current_exercise["ExerciseID"]:
                                color = "lightblue"
                                button.toggle()
                                button.setEnabled(False)
                            elif eval(self.exercises[index]["Seen"]):
                                grade = [entry["Grade"] for entry in self.exercises if self.exercises[index]["ExerciseID"] == entry["ExerciseID"]][0]
                                if grade in Config.EXERCISE_GRADE_COLORS.keys() and datetime.strptime(self.exercises[index]["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
                                    color = "rgb" + str(Config.EXERCISE_GRADE_COLORS[grade])
                                else:
                                    color = "gray"
                            else:
                                color = "white"
                            button.clicked.connect(lambda state, next_num=int(button.text()): self.processGrade(None, "Cond3", desired_next_num=next_num))
                        else:
                            color = "lightgray"
                            button.toggle()
                            button.setEnabled(False)
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


