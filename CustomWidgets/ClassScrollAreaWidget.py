import ElementStyles
from PyQt5.QtWidgets import QScrollBar, QHBoxLayout, QLabel, QWidget, QListWidgetItem, QFrame, QPushButton, QCheckBox, QLineEdit, QVBoxLayout
from PyQt5.QtWidgets import QListWidget, QListView, QSizePolicy, QAbstractScrollArea
from PyQt5.QtGui import QPixmap, QColor, QIcon, QImage, QCursor, QPainter
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice,Qt, QObject, QSize
from PyQt5 import QtCore
import cv2
import numpy as np
import io
from PIL import Image
import Config

class ScrollAreaWidget():
    scroll_area_widget = None
    scroll_bar = None
    list_name = None

    def __init__(self, scroll_area_widget):
        self.scroll_area_widget = scroll_area_widget
        self.scroll_area_layout = scroll_area_widget.children()[0].children()[0].children()[0]
        self.scroll_area_widget.setWidgetResizable(True)
        self.scroll_area_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.count = 0

    def clear(self) -> None:
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def setList(self, query_table_name: str, query_entries: list, give_shadow=True, vertical_spacing=3) -> None:
        self.clear()
        self.list_name = query_table_name
        self.give_shadow = give_shadow
        self.vertical_spacing = vertical_spacing
        for entry in query_entries:
            listitem = self.createWidget(query_table_name, entry)
            listitem.setFixedHeight(33)
            self.scroll_area_layout.addWidget(listitem)
            self.count += 1
        self.scroll_area_layout.setSpacing(self.vertical_spacing)
        self.scroll_area_layout.addStretch()
        #self.scroll_bar = QScrollBar()
        #self.scroll_bar.setStyleSheet("background : white;")
        #self.list_widget.setVerticalScrollBar(self.scroll_bar)


    def createWidget(self, query_table_name: str, entry) -> QWidget:
        elementLayout = QHBoxLayout()

        if query_table_name == "Study Lists":
            elementLayout.setContentsMargins(0, 5, 5, 5)

            label = QLabel()
            pix = QPixmap(Config.DRAG_HANDLE)
            pix = pix.scaled(15, 15, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            label.setPixmap(pix)
            elementLayout.addWidget(label)

            labelempty = QLabel()
            labelempty.setText("")
            labelempty.setFixedWidth(5)
            elementLayout.addWidget(labelempty)

            checkbox = QCheckBox()
            checkbox.setFixedWidth(13)
            elementLayout.addWidget(checkbox)

            labelempty = QLabel()
            labelempty.setText("")
            labelempty.setFixedWidth(25)
            elementLayout.addWidget(labelempty)

            label = QLabel()
            label.setText(entry["StudyListName"])
            label.setStyleSheet("color: #4e5256")
            label.setFixedWidth(100)
            elementLayout.addWidget(label)

            labelempty = QLabel()
            labelempty.setText("")
            labelempty.setFixedWidth(25)
            elementLayout.addWidget(labelempty)

            progress_label = QLabel()
            self.updateProgressBar(progress_label, entry)
            elementLayout.addWidget(progress_label)

            labelempty = QLabel()
            labelempty.setText("")
            labelempty.setFixedWidth(25)
            elementLayout.addWidget(labelempty)


            button_rename = QPushButton("Rename")
            button_rename.setFixedWidth(50)
            elementLayout.addWidget(button_rename)

            # labelempty = QLabel()
            # labelempty.setText("")
            # labelempty.setFixedWidth(25)
            # elementLayout.addWidget(labelempty)

            # buttondelete = QPushButton("Delete")
            # buttondelete.setFixedWidth(50)
            # elementLayout.addWidget(buttondelete)

        elif query_table_name == "Study List Collections":
            elementLayout.setContentsMargins(0, 0, 0, 0)

            vboxLayout = QVBoxLayout()
            vboxLayout.setSpacing(0)
            vboxLayout.setContentsMargins(0, 0, 0, 0)

            hboxLayout = QHBoxLayout()
            hboxLayout.setContentsMargins(5, 5, 5, 5)

            label = QLabel()
            pix = QPixmap(Config.RIGHT_ARROW)
            pix = pix.scaled(15, 15, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            label.setPixmap(pix)
            label.setFixedWidth(25)
            hboxLayout.addWidget(label)

            #label.setFixedHeight(23)

            label = QLabel()
            label.setText(entry["CollectionName"])
            label.setFixedWidth(350)
            label.setStyleSheet("color: #4e5256")
            hboxLayout.addWidget(label)

            label.setFixedHeight(33)


            label = QLabel()
            label.setText("")
            label.setFixedWidth(25)
            hboxLayout.addWidget(label)

            label = QLabel()
            label.setText(str(len(entry["Tags"].split(","))))
            label.setStyleSheet("color: #4e5256")
            hboxLayout.addWidget(label)

            widget = QWidget()
            widget.setLayout(hboxLayout)
            widget.setFixedHeight(33)
            # children = widget.children()
            # for i in range(1, len(children)):
            #     children[i].setWindowFlags(QtCore.Qt.FramelessWindowHint)
            #     children[i].setAttribute(QtCore.Qt.WA_TranslucentBackground)
            vboxLayout.addWidget(widget)

            widget = QWidget()
            widget.setLayout(vboxLayout)
            elementLayout.addWidget(widget)









        # rowLabel = QLabel()
        # elementLayout.addStretch()
        # elementLayout.addWidget(rowLabel)

        #elementLayout.setContentsMargins(5, 5, 5, 5)
        elementLayout.setSpacing(0)

        widget = QWidget()
        widget.setLayout(elementLayout)
        widget.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        #ElementStyles.hoverEffect(widget)
        self.setTranlucentAndFrameless(widget)
        if self.give_shadow:
            ElementStyles.regularShadow(widget)
        else:
            ElementStyles.lightShadow(widget)
            #widget.setStyleSheet("background-color: rgb(245, 245, 245);")

        #widget.setStyleSheet("border: solid lightgray; border-width: 0px 0px 1px 0px;")
        #ElementStyles.whiteRoundSquare(widget)
        ElementStyles.hoverEffect(widget)
        return widget

    def setTranlucentAndFrameless(self, widget):
        children = widget.children()
        if children is not None and len(children) > 0:
            for i in range(1, len(children)):
                children[i].setWindowFlags(QtCore.Qt.FramelessWindowHint)
                children[i].setAttribute(QtCore.Qt.WA_TranslucentBackground)
                self.setTranlucentAndFrameless(children[i])

    def updateProgressBar(self, progress_label, sect_entry):
        num_exercises = int(sect_entry["NumExercisesA"]) + int(sect_entry["NumExercisesB"]) + int(sect_entry["NumExercisesC"]) + int(sect_entry["NumExercisesD"]) + int(sect_entry["NumExercisesF"]) + int(sect_entry["NoGrade"])
        pb_length = 200
        white_rect = np.ones((8, pb_length), dtype=np.uint8) * 255
        white_rect_color = cv2.cvtColor(white_rect, cv2.COLOR_BGR2RGB)

        im_w_bg_bar = cv2.rectangle(white_rect_color, (0, 0), (pb_length, 8), Config.GREY_LIGHT_BLUE[::-1], -1)
        x_start = 0
        if num_exercises > 0:
            offset = int(np.floor((int(sect_entry["NumExercisesA"]) / num_exercises) * pb_length))
            if offset > 0:
                im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["A"][::-1], -1)
                x_start += offset + 1

            offset = int(np.floor((int(sect_entry["NumExercisesB"]) / num_exercises) * pb_length))
            if offset > 0:
                im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["B"][::-1], -1)
                x_start += offset + 1

            offset = int(np.floor((int(sect_entry["NumExercisesC"]) / num_exercises) * pb_length))
            if offset > 0:
                im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["C"][::-1], -1)
                x_start += offset + 1

            offset = int(np.floor((int(sect_entry["NumExercisesD"]) / num_exercises) * pb_length))
            if offset > 0:
                im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["D"][::-1], -1)
                x_start += offset + 1

            offset = int(np.floor((int(sect_entry["NumExercisesF"]) / num_exercises) * pb_length))
            if offset > 0:
                im_w_bg_bar = cv2.rectangle(im_w_bg_bar, (x_start, 0), (x_start + offset, 8), Config.EXERCISE_GRADE_COLORS["F"][::-1], -1)

        height, width, channel = im_w_bg_bar.shape
        bytesPerLine = channel * width
        qImg = QImage(im_w_bg_bar, width, height, bytesPerLine, QImage.Format_BGR888)
        solution_image_pixmap = QPixmap(qImg)
        progress_label.setPixmap(solution_image_pixmap)
        progress_label.setFixedWidth(225)
