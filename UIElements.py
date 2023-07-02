import ElementStyles
from PyQt5.QtWidgets import QScrollBar, QHBoxLayout, QLabel, QWidget, QListWidgetItem, QFrame, QPushButton
from PyQt5.QtGui import QPixmap, QColor, QIcon, QImage, QCursor
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice,Qt
from PyQt5 import QtCore
import cv2
import numpy as np
import io
from PIL import Image
import Config


class CounterElement():
    background_frame = None
    title_label = None
    value_label = None
    units_label = None

    def __init__(self, background_frame, title_label, value_label, units_label):
        self.background_frame = background_frame
        self.title_label = title_label
        self.value_label = value_label
        self.units_label = units_label
        ElementStyles.whiteRoundSquare(self.background_frame)
        ElementStyles.regularShadow(self.background_frame)


    def setValue(self, value):
        self.value_label.setText(str(value))

    def setTitle(self, title):
        self.title_label.setText(str(title))

    def setUnits(self, units):
        self.units_label.setText(str(units))



class IndicatorElement():
    background_frame = None
    title_label = None
    value_label = None

    def __init__(self, background_frame, title_label, value_label):
        self.background_frame = background_frame
        self.title_label = title_label
        self.value_label = value_label
        ElementStyles.whiteRoundSquare(self.background_frame)
        ElementStyles.regularShadow(self.background_frame)


    def setValue(self, value):
        self.value_label.setText(str(value))

    def setTitle(self, title):
        self.title_label.setText(str(title))




class ListElement():
    list_listwidget = None
    scroll_bar = None

    def __init__(self, list_listwidget):
        self.list_listwidget = list_listwidget

    def clear(self):
        self.list_listwidget.clear()


    def getItemIndex(self):
        return int(self.list_listwidget.currentItem().text())


    def setList(self, query_table_name, query_entries):
        self.list_listwidget.clear()
        row_number = 0
        for entry in query_entries:
            listitem = self.listItemElement(query_table_name, entry)
            self.insert(listitem)
        self.list_listwidget.setSpacing(3)
        self.scroll_bar = QScrollBar()
        self.scroll_bar.setStyleSheet("background : white;")
        self.list_listwidget.setVerticalScrollBar(self.scroll_bar)


    def insert(self, listItemElement):
        item = QListWidgetItem(self.list_listwidget)
        #item.setBackground(QColor('#eeeeec'))
        item.setSizeHint(listItemElement.sizeHint())
        item.setText(str(self.list_listwidget.count()))
        self.list_listwidget.setItemWidget(item, listItemElement)


    def listItemElement(self, query_table_name, entry):
        elementLayout = QHBoxLayout()

        if query_table_name == "Categories":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            IDLabel = QLabel()
            IDLabel.setText(entry["Category"])
            IDLabel.setFixedWidth(200)
            IDLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(IDLabel)

        elif query_table_name in "Textbooks":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            # IDLabel = QLabel()
            # IDLabel.setText(entry["ID"])
            # IDLabel.setFixedWidth(50)
            # IDLabel.setStyleSheet("color: #4e5256")
            # elementLayout.addWidget(IDLabel)

            authorLabel = QLabel()
            authorLabel.setText(entry["Authors"])
            authorLabel.setFixedWidth(80)
            authorLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(authorLabel)

            titleLabel = QLabel()
            titleLabel.setText(entry["Title"])
            titleLabel.setFixedWidth(320)
            titleLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(titleLabel)

            edLabel = QLabel()
            edLabel.setText(entry["Edition"])
            edLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(edLabel)

        elif query_table_name == "Study List":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            label = QLabel()
            label.setText(entry["StudyListName"])
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

        elif query_table_name == "Selected Study List Sections":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            label = QLabel()
            label.setText(entry[0])
            label.setFixedWidth(50)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry[1])
            label.setFixedWidth(50)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry[2])
            label.setFixedWidth(50)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            num_exercises = int(entry[3]["NumExercisesA"]) + int(entry[3]["NumExercisesB"]) + int(entry[3]["NumExercisesC"]) + int(entry[3]["NumExercisesD"]) + int(entry[3]["NumExercisesF"]) + int(entry[3]["NoGrade"])
            progress_label = QLabel()
            pb_length = 200
            white_rect = np.ones((8, pb_length), dtype=np.uint8) * 255
            white_rect_color = cv2.cvtColor(white_rect, cv2.COLOR_BGR2RGB)


            im_w_bg_bar = cv2.rectangle(white_rect_color, (0, 0), (pb_length, 8), Config.GREY_LIGHT_BLUE[::-1], -1)
            x_start = 0
            if num_exercises > 0:
                offset = int(np.floor((int(entry[3]["NumExercisesA"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["A"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry[3]["NumExercisesB"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["B"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry[3]["NumExercisesC"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["C"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry[3]["NumExercisesD"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["D"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry[3]["NumExercisesF"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["F"][::-1], -1)

            height, width, channel = im_w_bg_bar.shape
            bytesPerLine = channel * width
            qImg = QImage(im_w_bg_bar, width, height, bytesPerLine, QImage.Format_BGR888)
            solution_image_pixmap = QPixmap(qImg)
            progress_label.setPixmap(solution_image_pixmap)
            progress_label.setFixedWidth(225)
            elementLayout.addWidget(progress_label)

            button = QPushButton("Start")
            elementLayout.addWidget(button)
            button.setFixedWidth(50)

        elif query_table_name == "Sections for Extraction":
            elementLayout.setContentsMargins(0, 5, 0, 5)
            IDLabel = QLabel()
            IDLabel.setText(entry["ChapterNumber"])
            IDLabel.setAlignment(Qt.AlignCenter)
            IDLabel.setFixedWidth(25)
            IDLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(IDLabel)

            sectLabel = QLabel()
            sectLabel.setText(entry["SectionNumber"])
            sectLabel.setAlignment(Qt.AlignCenter)
            sectLabel.setFixedWidth(25)
            sectLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(sectLabel)


        elif query_table_name == "Sections":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            IDLabel = QLabel()
            IDLabel.setText(entry["ChapterNumber"])
            IDLabel.setFixedWidth(50)
            IDLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(IDLabel)

            sectLabel = QLabel()
            sectLabel.setText(entry["SectionNumber"])
            sectLabel.setFixedWidth(50)
            sectLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(sectLabel)

            label = QLabel()
            label.setText(str(entry["NumberOfSolutions"]))
            label.setFixedWidth(25)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            num_exercises = int(entry["NumExercisesA"]) + int(entry["NumExercisesB"]) + int(entry["NumExercisesC"]) + int(entry["NumExercisesD"]) + int(entry["NumExercisesF"]) + int(entry["NoGrade"])
            progress_label = QLabel()
            pb_length = 200
            white_rect = np.ones((8, pb_length), dtype=np.uint8) * 255
            white_rect_color = cv2.cvtColor(white_rect, cv2.COLOR_BGR2RGB)

            im_w_bg_bar = cv2.rectangle(white_rect_color, (0, 0), (pb_length, 8), Config.GREY_LIGHT_BLUE[::-1], -1)
            x_start = 0
            if num_exercises > 0:
                offset = int(np.floor((int(entry["NumExercisesA"])/num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["A"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry["NumExercisesB"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["B"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry["NumExercisesC"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["C"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry["NumExercisesD"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["D"][::-1], -1)
                    x_start += offset + 1

                offset = int(np.floor((int(entry["NumExercisesF"]) / num_exercises) * pb_length))
                if offset > 0:
                    im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["F"][::-1], -1)

            height, width, channel = im_w_bg_bar.shape
            bytesPerLine = channel * width
            qImg = QImage(im_w_bg_bar, width, height, bytesPerLine, QImage.Format_BGR888)
            solution_image_pixmap = QPixmap(qImg)
            progress_label.setPixmap(solution_image_pixmap)
            progress_label.setFixedWidth(225)
            elementLayout.addWidget(progress_label)

            button = QPushButton("Start")
            ElementStyles.lightShadow(button)
            elementLayout.addWidget(button)
            button.setFixedWidth(50)

            label = QLabel()
            label.setText("")
            label.setFixedWidth(25)
            elementLayout.addWidget(label)

            add_to_sl_button = QPushButton("Add to a Study List")
            ElementStyles.lightShadow(add_to_sl_button)
            elementLayout.addWidget(add_to_sl_button)


        elif query_table_name == "Exercises for Extraction":
            elementLayout.setContentsMargins(0, 0, 0, 0)
            pngLabel = QLabel()
            pngLabel.setText(str(entry))
            pngLabel.setAlignment(QtCore.Qt.AlignCenter)
            pngLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(pngLabel)
            button = QPushButton("Unmasked")
            button.setCheckable(True)
            button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            elementLayout.addWidget(button)
            button = QPushButton("Masked")
            button.setCheckable(True)
            button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            elementLayout.addWidget(button)
            button = QPushButton("Solution")
            button.setCheckable(True)
            button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            elementLayout.addWidget(button)

        elif query_table_name == "Flashcard Collections":
            elementLayout.setContentsMargins(5, 5, 5, 5)

            label = QLabel()
            label.setText(entry["Category"])
            label.setFixedWidth(205)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["Authors"])
            label.setFixedWidth(60)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["Title"])
            label.setFixedWidth(300)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["Edition"])
            #label.setFixedWidth(300)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

        elif query_table_name == "Flashcard Sets":
            elementLayout.setContentsMargins(5, 5, 5, 5)

            label = QLabel()
            label.setText(entry[0])
            label.setFixedWidth(20)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry[1])
            label.setFixedWidth(20)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            progress_label = QLabel()
            pb_length = 200
            white_rect = np.ones((8, pb_length), dtype=np.uint8) * 255
            white_rect_color = cv2.cvtColor(white_rect, cv2.COLOR_BGR2RGB)

            im_w_bg_bar = cv2.rectangle(white_rect_color, (0, 0), (pb_length, 8), Config.GREY_LIGHT_BLUE[::-1], -1)
            ####################################
            ####################################
            height, width, channel = im_w_bg_bar.shape
            bytesPerLine = channel * width
            qImg = QImage(im_w_bg_bar, width, height, bytesPerLine, QImage.Format_BGR888)
            solution_image_pixmap = QPixmap(qImg)
            progress_label.setPixmap(solution_image_pixmap)
            progress_label.setFixedWidth(225)
            elementLayout.addWidget(progress_label)

        elif query_table_name == "Set Flashcards":
            elementLayout.setContentsMargins(0, 0, 0, 0)
            label = QLabel()
            label.setText("Flashcard " + entry["FlashcardID"])
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("color: #4e5256")
            label.setFixedHeight(25)
            elementLayout.addWidget(label)
            label = QLabel()
            label.setText("Last Edited " + entry["LastEdited"])
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("color: #4e5256")
            label.setFixedHeight(25)
            elementLayout.addWidget(label)

        # rowLabel = QLabel()
        # elementLayout.addStretch()
        # elementLayout.addWidget(rowLabel)

        #elementLayout.setContentsMargins(5, 5, 5, 5)
        elementLayout.setSpacing(0)

        widget = QWidget()
        widget.setLayout(elementLayout)
        widget.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        ElementStyles.hoverEffect(widget)
        children = widget.children()
        for i in range(1, len(children)):
            children[i].setWindowFlags(QtCore.Qt.FramelessWindowHint)
            children[i].setAttribute(QtCore.Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(widget)
        #ElementStyles.whiteRoundSquare(widget)

        return widget


class ButtonElement():
    pushbutton = None
    def __init__(self, pushbutton):
        self.pushbutton = pushbutton
        pushbutton.__init__()
        ElementStyles.roundButton(self.pushbutton)
        ElementStyles.whiteBackground(self.pushbutton)
        ElementStyles.regularShadow(self.pushbutton)

    def setText(self, string):
        self.pushbutton.setText(string)

    def disconnect(self):
        self.pushbutton.clicked.disconnect()



class PageButtonElement():
    pushbutton = None
    def __init__(self, pushbutton):
        self.pushbutton = pushbutton
        ElementStyles.unselectedPageButton(self.pushbutton)

    def setText(self, string):
        self.pushbutton.setText(string)

    def setIcon(self, path):
        self.pushbutton.setIcon(QIcon(QPixmap(path)))
        self.pushbutton.setIconSize(QtCore.QSize(20, 20))









