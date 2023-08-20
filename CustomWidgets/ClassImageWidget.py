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
from ClassLabelWidget import LabelWidget

class ImageWidget(LabelWidget):
    label_widget = None

    def __init__(self, label_widget):
        super().__init__(label_widget)
        self.label_widget = label_widget

    def clear(self):
        self.label_widget.clear()

    def setImageFromArray(self, array):
        height, width, channel = array.shape
        bytesPerLine = channel * width
        qImg = QImage(array, width, height, bytesPerLine, QImage.Format_RGBX8888)
        image_pixmap = QPixmap(qImg)
        self.label_widget.setPixmap(image_pixmap)


    def setImageFromFilepath(self, filepath):
        pass

