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

class LabelWidget():
    label_widget = None

    def __init__(self, label_widget):
        self.label_widget = label_widget

    def clear(self) -> None:
        self.label_widget.clear()