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

class GridListWidget():
    label_widget = None

    def __init__(self, grid_layout):
        self.grid_layout = grid_layout

    def clearGrid(self) -> None:
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)


    def setGrid(self, page: str, parameters: list) -> None:
        if page == "StudyListPage":
            self.prev_selected_exercise_num = None
            self.clearGrid()
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

