import ElementStyles
from ContentPages.ClassPage import Page
from UIElements import ListElement
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QLabel, QHeaderView, QCheckBox, QPushButton
from PyQt5.QtGui import QFont, QCursor, QPixmap, QImage
from PyQt5.QtCore import Qt
import Config
import random
import string
from datetime import date
import matplotlib.pyplot as plt
import io
import numpy as np


class StudyFlashcardsPage(Page):

    def __init__(self, ui):
        Page.__init__(self, Config.StudyFlashcardsPage_page_number)
        self.ui = ui

    def objectReferences(self, edit_flashcards_page, flashcards_page):
        self.edit_flashcards_page = edit_flashcards_page
        self.flashcards_page = flashcards_page

    def showPage(self):
        self.ui.content_pages.setCurrentIndex(self.page_number)