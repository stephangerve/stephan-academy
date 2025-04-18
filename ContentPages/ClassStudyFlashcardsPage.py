from PyQt5 import uic
import ElementStyles
from ContentPages.ClassPage import Page
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QLabel, QHeaderView, QCheckBox, QPushButton
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from PyQt5.QtMultimedia import QSound, QSoundEffect
from PyQt5.QtGui import QFont, QCursor, QPixmap, QImage
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtCore import Qt
import Config
import random
import string
from datetime import date
import matplotlib.pyplot as plt
import io, os
import numpy as np
from datetime import date, timedelta, datetime
import random



class StudyFlashcardsPage(Page):
    ui = None
    exercises = None
    current_flashcard = None
    current_exercise_number = None
    MAX_TIME = 480  # 420
    WARNING_TIME = 120
    random.seed(datetime.now().timestamp())

    def __init__(self, content_pages):
        Page.__init__(self, Config.StudyFlashcardsPage_page_number)
        uic.loadUi('Resources/UI/study_flashcards_page.ui', self)
        self.content_pages = content_pages
        self.initUI()

    def initUI(self):
        self.skip_flashcard_button.clicked.connect(lambda state, grade=None: self.processGrade(grade, "Next"))
        self.sound_warning = QSoundEffect()
        self.sound_tick = QSoundEffect()
        self.sound_next = QSoundEffect()
        self.sound_warning.setSource(QUrl.fromLocalFile(Config.SOUND_WARNING))
        self.sound_tick.setSource(QUrl.fromLocalFile(Config.SOUND_TICK))
        self.sound_next.setSource(QUrl.fromLocalFile(Config.SOUND_NEXT))
        self.hide_timer = QTimer()
        self.start_hide_timer = QTimer()
        self.review_timer = QTimer()
        self.timer_counter = None


    def objectReferences(self, db_interface, edit_flashcards_page, flashcards_page):
        self.db_interface = db_interface
        self.edit_flashcards_page = edit_flashcards_page
        self.flashcards_page = flashcards_page

    def showPage(self, flashcards, flashcards_images_dir):
        self.flashcards = flashcards
        self.flashcards_numbers = [flashcard["FlashcardNumber"] for flashcard in self.flashcards]
        self.flashcards_images_dir = flashcards_images_dir
        self.clearNotificationLayout()
        self.timer_ticker.setStyleSheet("color: white;\nfont: 12pt;")
        self.disconnectWidget(self.exit_review_button)
        self.exit_review_button.clicked.connect(lambda: self.exitReview())
        f_num = random.choice(self.flashcards_numbers)
        self.current_flashcard = [flashcard for flashcard in self.flashcards if flashcard["FlashcardNumber"] == f_num][0]
        self.last_page_number = self.content_pages.currentIndex()
        self.content_pages.setCurrentIndex(self.page_number)
        self.reviewFlashcard()


    def exitReview(self):
        try:
            if self.review_timer.isActive():
                self.review_timer.disconnect()
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
        self.flashcards_page.selected_set_flashcards = self.flashcards
        self.content_pages.setCurrentIndex(self.last_page_number)
        return

    def clearNotificationLayout(self):
        for i in reversed(range(self.popup_note_layout.count())):
            self.popup_note_layout.itemAt(i).widget().setParent(None)


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
        self.popup_note_layout.addWidget(self.popup_label)
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
        self.timer_ticker.setText(str((datetime(1, 1, 1, 0, 0) + timedelta(seconds=self.timer_counter)).strftime("%M:%S")))
        if self.timer_counter == self.WARNING_TIME:
            self.sound_warning.play()
            self.showNotification("Two Minutes Left!")
        if self.timer_counter <= self.WARNING_TIME:
            self.timer_ticker.setStyleSheet("color: red;\nfont: 12pt;")
        if 0 < self.timer_counter < 10:
            self.sound_tick.play()
        if self.timer_counter == 0:
            self.review_timer.disconnect()
            self.processGrade(None, "Next")

    def reviewFlashcard(self):
        self.sound_next.play()
        try:
            if self.review_timer.isActive():
                self.review_timer.disconnect()
        except:
            pass
        self.timer_ticker.setText(str((datetime(1, 1, 1, 0, 0) + timedelta(seconds=self.MAX_TIME)).strftime("%M:%S")))
        self.timer_ticker.setStyleSheet("color: white;\nfont: 12pt;")
        self.front_flashcard_pic_label.clear()
        self.back_flashcard_pic_label.clear()
        for i in reversed(range(self.button_hboxlayout.count())):
            self.button_hboxlayout.itemAt(i).widget().setParent(None)
        front_flashcard_path = os.path.join(self.flashcards_images_dir, self.current_flashcard["FlashcardNumber"] + " - flashcard _front.png")
        front_flashcard_image_pixmap = QPixmap(front_flashcard_path)
        if front_flashcard_image_pixmap.size().height() > self.front_flashcard_pic_label.size().height():
            front_flashcard_image_pixmap = front_flashcard_image_pixmap.scaled(front_flashcard_image_pixmap.size().width(), self.front_flashcard_pic_label.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.front_flashcard_pic_label.setPixmap(front_flashcard_image_pixmap)

        #self.front_flashcard_pic_label.resize(front_flashcard_pic_label.width(), front_flashcard_pic_label.height())
        #self.problem_pic_scroll_area.verticalScrollBar().setValue(0)


        button = QPushButton("Show Back")
        button.resize(50, 50)
        button.clicked.connect(lambda state: self.finishedReview())
        self.button_hboxlayout.addWidget(button)
        self.timer_counter = self.MAX_TIME
        self.review_timer.start(1000)
        self.review_timer.timeout.connect(lambda: self.updateTimerTicker())

        ElementStyles.regularShadow(self.front_flashcard_pic_label)
        ElementStyles.removeShadow(self.back_flashcard_pic_label)

        self.cards_counter.setText(str(len(self.flashcards_numbers)) + "/" + str(len(self.flashcards)))

    def finishedReview(self):
        self.review_timer.disconnect()
        back_flashcard_path = os.path.join(self.flashcards_images_dir, self.current_flashcard["FlashcardNumber"] + " - flashcard back.png")
        back_flashcard_image_pixmap = QPixmap(back_flashcard_path)
        if back_flashcard_image_pixmap.size().height() > self.back_flashcard_pic_label.size().height():
            back_flashcard_image_pixmap = back_flashcard_image_pixmap.scaled(back_flashcard_image_pixmap.size().width(), self.back_flashcard_pic_label.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.back_flashcard_pic_label.setPixmap(back_flashcard_image_pixmap)
        self.button_hboxlayout.itemAt(0).widget().setParent(None)
        for grade in Config.EXERCISE_GRADE_COLORS.keys():
            button = QPushButton(grade)
            button.setStyleSheet("background-color : rgb" + str(Config.EXERCISE_GRADE_COLORS[grade]))
            button.clicked.connect(lambda state, grade=button.text(): self.processGrade(grade, "Next"))
            self.button_hboxlayout.addWidget(button)

        ElementStyles.regularShadow(self.back_flashcard_pic_label)


    def processGrade(self, grade, direction):
        self.flashcards_numbers.remove(self.current_flashcard["FlashcardNumber"])
        self.current_flashcard["Seen"] = 'True'
        if grade is not None:
            self.current_flashcard["Attempts"] += 1
            self.current_flashcard["LastAttempted"] = date.today().strftime("%m/%d/%Y")
            self.current_flashcard["LastAttemptTime"] = datetime.now().strftime("%H:%M")
            self.current_flashcard["Grade"] = grade
            old_avg_time = 0
            if int(self.current_flashcard["Attempts"]) - 1 >= 1:
                if self.current_flashcard["AverageTime"] is not None:
                    old_avg_time = float(self.current_flashcard["AverageTime"])
                else:
                    old_avg_time = 0
            self.current_flashcard["AverageTime"] = (((self.MAX_TIME - self.timer_counter)/60) + old_avg_time * (int(self.current_flashcard["Attempts"]) - 1)) / int(self.current_flashcard["Attempts"]) #derivation of formula in notepad on desk
        if self.current_flashcard["AverageTime"] == '':
            self.current_flashcard["AverageTime"] = 0.0
        update_params = [self.current_flashcard["Seen"],
                         self.current_flashcard["Attempts"],
                         self.current_flashcard["LastAttempted"],
                         self.current_flashcard["LastAttemptTime"],
                         self.current_flashcard["Grade"],
                         self.current_flashcard["AverageTime"],
                         self.current_flashcard["CollectionID"],
                         self.current_flashcard["SetID"],
                         self.current_flashcard["FlashcardNumber"]]
        self.db_interface.updateEntry("Flashcard", update_params)
        self.showNotification("Attempt saved")
        if direction == "Next":
            if len(self.flashcards_numbers) > 0:
                f_num = random.choice(self.flashcards_numbers)
                self.current_flashcard = [flashcard for flashcard in self.flashcards if flashcard["FlashcardNumber"] == f_num][0]
                self.reviewFlashcard()
            else:
                self.exitReview()




