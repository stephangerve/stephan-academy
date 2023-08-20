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

class PushButtonWidget():
    button_widget = None

    def __init__(self, button_widget):
        self.button_widget = button_widget

    def disconnect(self) -> None:
        try:
            self.button_widget.clicked.disconnect()
        except:
            pass

    def connect(self, func, parameters) -> None:
        pass