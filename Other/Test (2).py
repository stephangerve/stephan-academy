from PyQt5.QtWidgets import QScrollBar, QHBoxLayout, QLabel, QWidget, QListWidgetItem, QFrame, QMainWindow, QVBoxLayout
from PyQt5.QtGui import QPixmap, QColor, QIcon, QImage
from PyQt5 import QtCore
import cv2
import numpy as np
from PyQt5 import uic
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets



if __name__ == "__main__":
    app = QApplication(sys.argv)
    progress_label = QLabel()
    color = (0, 0, 255)
    height, width = 5, 500
    white_rect = np.ones((height, width), dtype=np.uint8) * 255
    #white_rect = np.zeros((height, width, 3), dtype=np.uint8)
    # white_rect[..., 0] = 255
    # white_rect[..., 1] = 255
    # white_rect[..., 2] = 255
    white_rect_color = cv2.cvtColor(white_rect, cv2.COLOR_BGRA2RGBA)
    im_w_bg_bar = cv2.rectangle(white_rect_color, (0, 0), (500, 5), color, -1)
    height, width, channel = im_w_bg_bar.shape
    bytesPerLine = 3 * width
    qImg = QImage(im_w_bg_bar, width, height, bytesPerLine, QImage.Format_RGB888)
    solution_image_pixmap = QPixmap(qImg.copy())
    progress_label.setPixmap(solution_image_pixmap)
    vbox = QVBoxLayout()
    vbox.addWidget(progress_label)
    win = QWidget()
    win.setLayout(vbox)
    win.show()
    sys.exit(app.exec_())
