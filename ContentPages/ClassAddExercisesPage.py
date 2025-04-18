from PyQt5 import uic
from ClassImageExtractor import ImageExtractor
from ContentPages.ClassPage import Page
from PyQt5.QtGui import QPixmap, QKeyEvent, QKeySequence, QCursor, QMouseEvent, QImage
from PyQt5.QtWidgets import QShortcut, QAction, QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QAbstractButton, QHBoxLayout, QFrame
from PyQt5.QtCore import QEvent, Qt, QTimer, QSize
from PyQt5 import QtCore
import ElementStyles
import os
import Config
import inflect
import keyboard
import time
import shutil
from functools import partial
from PIL import Image
import numpy as np
p = inflect.engine()

class AddExercisesPage(Page, QWidget):
    ui = None
    exercise_stats = None
    one_column_boundary_set = False
    two_columns_boundary_set = False
    image_indices = []



    def __init__(self, content_pages):
        Page.__init__(self, Config.AddExercisesPage_page_number)
        uic.loadUi('Resources/UI/add_exercises_page.ui', self)
        self.content_pages = content_pages
        self.default_starting_index_spinbox.setValue(1)
        self.default_idx_inc_spinbox.setValue(1)
        self.bbox_scan_radius_spinbox.setValue(Config.DEFAULT_SCAN_RADIUS_BBOX)
        self.mask_scan_radius_spinbox.setValue(Config.DEFAULT_SCAN_RADIUS_MASK)
        self.grid_column_line_scan_radius_spinbox.setValue(Config.DEFAULT_SCAN_RADIUS_GRID_COL)
        self.grid_column_bbox_scan_radius_spinbox.setValue(Config.DEFAULT_SCAN_RADIUS_BBOX)
        self.column_line_scan_radius_spinbox.setValue(Config.DEFAULT_SCAN_RADIUS_COL_LINE)
        self.scan_row_avg_color_threshold_spinbox.setValue(Config.DEFAULT_SCAN_ROW_AVERAGE_COLOR_THRESHOLD)
        self.bin_search_white_threshold_spinbox.setValue(Config.DEFAULT_BIN_SEARCH_WHITE_THRESHOLD)
        self.event_handlers = []
        self.extracted_images_timer = QTimer()
        self.images_in_grid = {}
        self.prev_selected_extracted_image_widget = None
        self.prev_selected_section_widget = None
        self.extracted_image_arrays = {}
        self.IMAGE_TYPE = "Exercises"
        self.button_m = None
        self.button_u = None
        self.last_chap_num = None
        self.current_set_index = None

    def objectReferences(self, db_interface, learning_page):
        self.db_interface = db_interface
        self.learning_page = learning_page

    def showPage(self, textbook_sections, selected_textbook_ID, selected_category, selected_author, selected_textbook_title, selected_edition):
        # ElementStyles.regularShadow(self.ch_sect_header_label)
        # ElementStyles.regularShadow(self.textbook_info_header_label)
        # ElementStyles.regularShadow(self.saved_images_header_label)
        self.current_set_index = None
        self.saved_images_listwidget.clear()
        self.png_label.clear()
        self.clearExerciseImageButtonsLayout()
        self.selected_textbook_ID = selected_textbook_ID
        self.selected_category = selected_category
        self.selected_author = selected_author
        self.selected_textbook_title = selected_textbook_title
        self.selected_edition = selected_edition
        self.textbook_sections = textbook_sections
        self.current_chap_num = self.textbook_sections[0]["ChapterNumber"]
        #self.makeEPackDirForTextbook(selected_textbook_ID, selected_category, selected_author, selected_textbook_title, selected_edition)
        self.image_extractor = ImageExtractor(self, self.extracted_image_arrays)
        self.add_exercises_sections_listwidget.clear()
        self.prev_selected_extracted_image_widget = None
        self.prev_selected_section_widget = None
        self.add_exercises_sections_listwidget.setList("Sections for Extraction", self.textbook_sections)
        self.disconnectWidget(self.add_exercises_sections_listwidget)
        self.add_exercises_sections_listwidget.itemClicked.connect(lambda: self.sectionsEntryClicked(int(self.add_exercises_sections_listwidget.currentItem().text()) - 1))
        self.changeMode(0)
        self.extract_exercises_button.clicked.connect(lambda: self.changeMode(0))
        self.extract_solutions_button.clicked.connect(lambda: self.changeMode(1))
        self.delete_button.clicked.connect(lambda: self.deleteImageEntry())
        if self.selected_edition != "1st":
            self.e_packs_txtbk_dir = os.path.join(Config.E_PACKS_DIR, self.selected_category, " - ".join([self.selected_author, self.selected_textbook_title, self.selected_edition]))
            self.txtbk_dir = os.path.join(Config.MAIN_DIR, self.selected_category, " - ".join([self.selected_author, self.selected_textbook_title, self.selected_edition]), "Textbook")
            self.sm_dir = os.path.join(Config.MAIN_DIR, self.selected_category, " - ".join([self.selected_author, self.selected_textbook_title, self.selected_edition]), "Solutions Manual")
        else:
            self.e_packs_txtbk_dir = os.path.join(Config.E_PACKS_DIR, self.selected_category, " - ".join([self.selected_author, self.selected_textbook_title]))
            self.txtbk_dir = os.path.join(Config.MAIN_DIR, self.selected_category, " - ".join([self.selected_author, self.selected_textbook_title]), "Textbook")
            self.sm_dir = os.path.join(Config.MAIN_DIR, self.selected_category, " - ".join([self.selected_author, self.selected_textbook_title]), "Solutions Manual")
        self.disconnectWidget(self.open_ei_dir_button)
        self.disconnectWidget(self.open_si_dir_button)
        self.open_ei_dir_button.clicked.connect(lambda: os.startfile(os.path.join(self.e_packs_txtbk_dir, "Exercises Images")))
        self.open_si_dir_button.clicked.connect(lambda: os.startfile(os.path.join(self.e_packs_txtbk_dir, "Solutions Images")))
        self.disconnectWidget(self.open_txtbk_dir_button)
        self.disconnectWidget(self.open_sm_dir_button)
        self.open_txtbk_dir_button.clicked.connect(lambda: os.startfile(self.txtbk_dir))
        self.open_sm_dir_button.clicked.connect(lambda: os.startfile(self.sm_dir))
        self.extracted_images_timer.start(1000)
        self.extracted_images_timer.timeout.connect(lambda: self.updateExtractedImagesGrid())
        ElementStyles.regularShadow(self.frame_a1)
        ElementStyles.regularShadow(self.frame_a2)
        ElementStyles.regularShadow(self.frame_a3)
        ElementStyles.regularShadow(self.frame_a4)
        ElementStyles.regularShadow(self.frame_a5)
        ElementStyles.regularShadow(self.frame_a6)
        self.extracted_images_scrollArea.setWidgetResizable(True)
        #extracted_images_bg_widget = QWidget()
        #extracted_images_gridlayout = QGridLayout()
        # for i in range(50):
        #     for j in range(3):
        #         widget = QWidget()
        #         widget.setStyleSheet("background-color: #ffffff")
        #         widget.setFixedSize(200, 80)
        #         ElementStyles.lightShadow(widget)
        #         self.extracted_images_gridlayout.addWidget(widget, i, j)
        #extracted_images_bg_widget.setLayout(extracted_images_gridlayout)
        #self.extracted_images_scrollArea.setWidget(extracted_images_bg_widget)
        self.prev_listwidgetitem_widget = None
        self.last_grid_row_idx = 0
        self.grid_col_start_idx = 0
        self.last_image_index = 1
        self.category_header_label.setText(selected_category)
        self.textbook_header_label.setText(" - ".join([selected_author, selected_textbook_title, selected_edition]))
        self.exit_add_ex_page_button.clicked.connect(lambda: self.exitPage())
        self.extracted_image_arrays.clear()
        self.images_in_grid.clear()
        self.content_pages.setCurrentIndex(self.page_number)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.extracted_images_gridlayout.count() > 0:
                childWidget = self.childAt(event.pos())
                while type(childWidget) != QWidget:
                    childWidget = childWidget.parent()
                if len(childWidget.children()) > 0:
                    try:
                        if type(childWidget.children()[2]) == QLabel:
                            if "Exercise" in childWidget.children()[2].text() or "Solution" in childWidget.children()[2].text():
                                self.extractedImageEntryClicked(childWidget)
                    except:
                        pass


    def exitPage(self):
        self.content_pages.setCurrentIndex(self.learning_page.page_number)
        return

    def changeMode(self, mode):
        if mode == 0:
            self.IMAGE_TYPE = "Exercises"
            self.extract_exercises_button.setEnabled(False)
            if not self.extract_exercises_button.isChecked():
                self.extract_exercises_button.toggle()
            if self.extract_solutions_button.isChecked():
                self.extract_solutions_button.toggle()
                self.extract_solutions_button.setEnabled(True)
        elif mode == 1:
            self.IMAGE_TYPE = "Solutions"
            self.extract_solutions_button.setEnabled(False)
            if not self.extract_solutions_button.isChecked():
                self.extract_solutions_button.toggle()
            if self.extract_exercises_button.isChecked():
                self.extract_exercises_button.toggle()
                self.extract_exercises_button.setEnabled(True)
        if self.current_set_index is not None:
            self.sectionsEntryClicked(self.current_set_index)

    def extractedImageWidget(self, image_index, image_array):
        widget_width = 200
        widget_height = 80
        if self.IMAGE_TYPE == "Exercises":
            np_image_array_u = np.array(image_array["unmasked"])
            height, width, channel = np_image_array_u.shape
            bytesPerLine = channel * width
            qImg_u = QImage(np_image_array_u, width, height, bytesPerLine, QImage.Format_RGBX8888)
            qpixmap_u = QPixmap(qImg_u)
            qpixmap_u = qpixmap_u.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            pic_u_label = QLabel()
            pic_u_label.setAlignment(Qt.AlignCenter)
            pic_u_label.setPixmap(qpixmap_u)
            ElementStyles.lightShadow(pic_u_label)

            np_image_array_m = np.array(image_array["masked"])
            height, width, channel = np_image_array_m.shape
            bytesPerLine = channel * width
            qImg_m = QImage(np_image_array_m, width, height, bytesPerLine, QImage.Format_RGBX8888)
            qpixmap_m = QPixmap(qImg_m)
            qpixmap_m = qpixmap_m.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            pic_m_label = QLabel()
            pic_m_label.setAlignment(Qt.AlignCenter)
            pic_m_label.setPixmap(qpixmap_m)
            ElementStyles.lightShadow(pic_m_label)

            hlayout = QHBoxLayout()
            hlayout.setContentsMargins(0, 0, 0, 0)
            hlayout.addWidget(pic_u_label)
            hlayout.addWidget(pic_m_label)

            frame = QFrame()
            frame.setLayout(hlayout)
            im_widget = frame
        else:
            np_image_array = np.array(image_array)
            height, width, channel = np_image_array.shape
            bytesPerLine = channel * width
            qImg = QImage(np_image_array, width, height, bytesPerLine, QImage.Format_RGBX8888)
            qpixmap = QPixmap(qImg)
            qpixmap = qpixmap.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

            pic_label = QLabel()
            pic_label.setPixmap(qpixmap)
            pic_label.setAlignment(Qt.AlignCenter)
            ElementStyles.lightShadow(pic_label)
            im_widget = pic_label

        fn_label = QLabel(self.IMAGE_TYPE[:-1] + " " + str(image_index))
        fn_label.setFixedSize(widget_width, 20)
        fn_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(im_widget)
        layout.addWidget(fn_label)
        widget = QWidget()
        close_button = QPushButton("X")
        #widget = QPushButton()
        #widget.setFlat(True)
        #widget.setWindowFlags(Qt.FramelessWindowHint)
        #widget.setAttribute(Qt.WA_TranslucentBackground)
        widget.setCursor(QCursor(Qt.PointingHandCursor))
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #ffffff")
        ElementStyles.hoverEffect(widget)
        widget.setFixedSize(widget_width, widget_height)
        self.setTranlucentAndFrameless(widget)
        return widget

    def setTranlucentAndFrameless(self, widget):
        children = widget.children()
        if children is not None and len(children) > 0:
            for i in range(1, len(children)):
                children[i].setWindowFlags(QtCore.Qt.FramelessWindowHint)
                children[i].setAttribute(QtCore.Qt.WA_TranslucentBackground)
                self.setTranlucentAndFrameless(children[i])

    def updateExtractedImagesGrid(self):
        count = len(self.extracted_image_arrays)
        self.extracted_images_label.setText("Extracted Images: " + str(count))
        MAX_COLS = 3
        if (len(self.extracted_image_arrays) - len(self.images_in_grid)) > 0:
            for idx in self.extracted_image_arrays.keys():
                if idx not in list(self.images_in_grid.keys()):
                    self.images_in_grid[idx] = self.extracted_image_arrays[idx]
            if count % MAX_COLS == 0:
                rows = int(count / MAX_COLS)
            else:
                rows = int(count / MAX_COLS) + 1
            for i in range(self.last_grid_row_idx, rows):
                self.last_grid_row_idx = i
                if int(count / ((i + 1) * MAX_COLS)) > 0:
                    columns = MAX_COLS
                elif i > 0:
                    columns = count % (i * MAX_COLS)
                else:
                    columns = count
                for j in range(self.grid_col_start_idx, columns):
                    index = i * MAX_COLS + j
                    self.grid_col_start_idx = j
                    widget = self.extractedImageWidget(list(self.images_in_grid.keys())[index], list(self.images_in_grid.values())[index])
                    self.extracted_images_gridlayout.addWidget(widget, i, j)
                    #print(self.extracted_images_gridlayout.itemAtPosition(i, j).widget().children()[2].text())
                if self.grid_col_start_idx == MAX_COLS - 1:
                    self.grid_col_start_idx = 0
            self.grid_col_start_idx += 1
        elif len(self.images_in_grid) > len(self.extracted_image_arrays):
            oldCount = len(self.images_in_grid)
            for image in self.images_in_grid:
                if image not in list(self.extracted_image_arrays.values()):
                    idx = self.images_in_grid.index(image)
                    self.images_in_grid.pop(idx)
                    self.extracted_images_gridlayout.itemAt(idx).widget().setParent(None)

            if oldCount % MAX_COLS == 0:
                rows = int(oldCount / MAX_COLS)
            else:
                rows = int(oldCount / MAX_COLS) + 1
            for i in range(rows):
                if count > 0:
                    self.last_grid_row_idx = i
                    if int(oldCount / ((i + 1) * MAX_COLS)) > 0:
                        columns = MAX_COLS
                    elif i > 0:
                        columns = oldCount % (i * MAX_COLS)
                    else:
                        columns = oldCount
                    for j in range(columns):
                        if count > 0:
                            if self.extracted_images_gridlayout.itemAtPosition(i, j) is None:
                                M = j + 1
                                for k in range(i, rows):
                                    if int(oldCount / ((k + 1) * MAX_COLS)) > 0:
                                        columns = MAX_COLS
                                    elif k > 0:
                                        columns = oldCount % (k * MAX_COLS)
                                    else:
                                        columns = oldCount
                                    for l in range(M, columns):
                                        if self.extracted_images_gridlayout.itemAtPosition(k, l) is not None:
                                            widget = self.extracted_images_gridlayout.itemAtPosition(k, l).widget()
                                            widget.setParent(None)
                                            self.extracted_images_gridlayout.addWidget(widget, i, j)
                                            break
                                    if self.extracted_images_gridlayout.itemAtPosition(i, j) is not None:
                                        break
                                    else:
                                        M = 0
                            count -= 1
                        else:
                            break
                else:
                    break
        if len(self.images_in_grid) > 0:
            widget_width = 200
            widget_height = 80
            keys = iter(self.extracted_image_arrays.keys())
            if len(self.extracted_image_arrays) % MAX_COLS == 0:
                last_row_count = MAX_COLS
            else:
                last_row_count = len(self.extracted_image_arrays) % MAX_COLS
            #M = int(np.ceil(self.extracted_images_gridlayout.count()/MAX_COLS))
            M = int(np.ceil(len(self.extracted_image_arrays)/MAX_COLS))
            for i in range(M):
                if i == M - 1:
                    N = last_row_count
                else:
                    N = MAX_COLS
                for j in range(N):
                    try:
                        key = next(keys)
                        if self.extracted_image_arrays[key] != self.images_in_grid[key]:
                            if self.IMAGE_TYPE == "Exercises":
                                np_image_array_u = np.array(self.extracted_image_arrays[key]["unmasked"])
                                height, width, channel = np_image_array_u.shape
                                bytesPerLine = channel * width
                                qImg_u = QImage(np_image_array_u, width, height, bytesPerLine, QImage.Format_RGBX8888)
                                qpixmap_u = QPixmap(qImg_u)
                                qpixmap_u = qpixmap_u.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
                                pic_u_label = self.extracted_images_gridlayout.itemAtPosition(i, j).widget().children()[1].children()[1]
                                pic_u_label.setAlignment(Qt.AlignCenter)
                                pic_u_label.setPixmap(qpixmap_u)
                                pic_u_label.setWindowFlags(Qt.FramelessWindowHint)
                                pic_u_label.setAttribute(Qt.WA_TranslucentBackground)
                                ElementStyles.lightShadow(pic_u_label)

                                np_image_array_m = np.array(self.extracted_image_arrays[key]["masked"])
                                height, width, channel = np_image_array_m.shape
                                bytesPerLine = channel * width
                                qImg_u = QImage(np_image_array_u, width, height, bytesPerLine, QImage.Format_RGBX8888)
                                qpixmap_u = QPixmap(qImg_u)
                                qpixmap_u = qpixmap_u.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
                                pic_u_label = self.extracted_images_gridlayout.itemAtPosition(i, j).widget().children()[1].children()[2]
                                pic_u_label.setAlignment(Qt.AlignCenter)
                                pic_u_label.setPixmap(qpixmap_u)
                                pic_u_label.setWindowFlags(Qt.FramelessWindowHint)
                                pic_u_label.setAttribute(Qt.WA_TranslucentBackground)
                                ElementStyles.lightShadow(pic_u_label)


                            elif self.IMAGE_TYPE == "Solutions":
                                np_image_array = np.array(self.extracted_image_arrays[key])
                                height, width, channel = np_image_array.shape
                                bytesPerLine = channel * width
                                qImg = QImage(np_image_array, width, height, bytesPerLine, QImage.Format_RGBX8888)
                                qpixmap = QPixmap(qImg)
                                qpixmap = qpixmap.scaled(widget_width, widget_height - 40, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

                                pic_label = self.extracted_images_gridlayout.itemAtPosition(i, j).widget().children()[1]
                                pic_label.setPixmap(qpixmap)
                                pic_label.setAlignment(Qt.AlignCenter)
                                pic_label.setWindowFlags(Qt.FramelessWindowHint)
                                pic_label.setAttribute(Qt.WA_TranslucentBackground)
                                ElementStyles.lightShadow(pic_label)

                            self.images_in_grid[key] = self.extracted_image_arrays[key]
                    except:
                        pass
                        pass

    def clearImagesGrid(self):
        self.last_grid_row_idx = 0
        self.grid_col_start_idx = 0
        self.extracted_images_label.setText("Extracted Images: 0")
        for i in reversed(range(self.extracted_images_gridlayout.count())):
            self.extracted_images_gridlayout.itemAt(i).widget().setParent(None)
            #self.extracted_images_gridlayout.removeWidget(self.extracted_images_gridlayout.itemAt(i).widget())

    def sectionsEntryClicked(self, set_index):
        #if len(os.listdir(Config.TEMP_SS_PATH)) == 0:
        self.selected_extracted_image_entry_index = None
        self.png_label.clear()
        self.clearExerciseImageButtonsLayout()
        if self.current_set_index != set_index:
            self.current_set_index = set_index
            selected_widget = self.add_exercises_sections_listwidget.itemWidget(self.add_exercises_sections_listwidget.item(self.current_set_index))
            ElementStyles.selectedListItem(selected_widget)
            if self.prev_selected_section_widget is not None:
                ElementStyles.unselectedListItem(self.prev_selected_section_widget)
            self.prev_selected_section_widget = selected_widget
        self.selected_chap_num = self.textbook_sections[self.current_set_index]["ChapterNumber"]
        self.selected_sect_num = self.textbook_sections[self.current_set_index]["SectionNumber"]
        self.selected_exercises = self.db_interface.fetchEntries("Exercises", [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num])
        # self.exercise_images = [entry["UnmaskedExercisePath"].split(" -- ")[-1] for entry in self.selected_exercises if entry["UnmaskedExercisePath"] is not None]
        # self.exercise_images += [entry["MaskedExercisePath"].split(" -- ")[-1] for entry in self.selected_exercises if entry["MaskedExercisePath"] is not None]
        # self.exercise_images.sort()
        self.exercise_numbers = [entry["ExerciseNumber"] for entry in self.selected_exercises]
        self.exercise_numbers.sort()
        self.selected_exercises_dict = dict(zip(self.exercise_numbers, self.selected_exercises))
        self.saved_images_listwidget.setList("Exercises for Extraction", self.exercise_numbers)
        self.disconnectWidget(self.saved_images_listwidget)
        self.saved_images_listwidget.itemClicked.connect(lambda: self.savedImageEntryClicked(self.saved_images_listwidget.currentItem(), "Unmasked"))
        for i in range(self.saved_images_listwidget.count()):
            self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-3].clicked.connect(lambda state, i=i: self.savedImageEntryClicked(self.saved_images_listwidget.item(i), "Unmasked"))
            self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-2].clicked.connect(lambda state, i=i: self.savedImageEntryClicked(self.saved_images_listwidget.item(i), "Masked"))
            if self.selected_exercises_dict[int(self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[1].text())]["SolutionPath"] is not None \
            and self.selected_exercises_dict[int(self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[1].text())]["SolutionPath"] != "":
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-1].clicked.connect(lambda state, i=i: self.savedImageEntryClicked(self.saved_images_listwidget.item(i), "Solution"))
            else:
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).setCursor(QCursor(Qt.ArrowCursor))
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[1].setCursor(QCursor(Qt.PointingHandCursor))
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[2].setCursor(QCursor(Qt.PointingHandCursor))
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[3].setCursor(QCursor(Qt.PointingHandCursor))
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[4].setCursor(QCursor(Qt.ArrowCursor))
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-1].toggle()
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-1].setChecked(True)
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-1].setEnabled(False)
                self.saved_images_listwidget.itemWidget(self.saved_images_listwidget.item(i)).children()[-1].setStyleSheet("background-color: gray")
        self.annotateAndExtract(self.selected_chap_num, self.selected_sect_num)
        self.prev_listwidgetitem_widget = None

    def savedImageEntryClicked(self, listwidgetitem, type):
        #exercise_index = int(self.exercise_images[ui_list_index - 1].split(".")[-3])
        #exercise_index = self.exercise_numbers[ui_list_index - 1]
        listwidgetitem_widget = self.saved_images_listwidget.itemWidget(listwidgetitem)
        if self.prev_listwidgetitem_widget is not None:
            ElementStyles.unselectedListItem(self.prev_listwidgetitem_widget)
        ElementStyles.selectedListItem(listwidgetitem_widget)
        self.prev_listwidgetitem_widget = listwidgetitem_widget
        if type == "Unmasked":
            if not listwidgetitem_widget.children()[-3].isChecked():
                listwidgetitem_widget.children()[-3].toggle()
            listwidgetitem_widget.children()[-3].setChecked(True)
            listwidgetitem_widget.children()[-3].setEnabled(False)
            png_path = os.path.join(Config.E_PACKS_DIR, "\\".join(self.selected_exercises_dict[int(listwidgetitem_widget.children()[1].text())]["UnmaskedExercisePath"].split(" -- ")))
        elif type == "Masked":
            if not listwidgetitem_widget.children()[-2].isChecked():
                listwidgetitem_widget.children()[-2].toggle()
            listwidgetitem_widget.children()[-2].setChecked(True)
            listwidgetitem_widget.children()[-2].setEnabled(False)
            png_path = os.path.join(Config.E_PACKS_DIR, "\\".join(self.selected_exercises_dict[int(listwidgetitem_widget.children()[1].text())]["MaskedExercisePath"].split(" -- ")))
        elif type == "Solution":
            if not listwidgetitem_widget.children()[-1].isChecked():
                listwidgetitem_widget.children()[-1].toggle()
            listwidgetitem_widget.children()[-1].setChecked(True)
            listwidgetitem_widget.children()[-1].setEnabled(False)
            png_path = os.path.join(Config.E_PACKS_DIR, "\\".join(self.selected_exercises_dict[int(listwidgetitem_widget.children()[1].text())]["SolutionPath"].split(" -- ")))
        if self.prev_listwidgetitem_widget is not None and listwidgetitem_widget.children()[1].text() != self.prev_listwidgetitem_widget.children()[1].text():
            if self.prev_listwidgetitem_widget.children()[-3].isChecked():
                self.prev_listwidgetitem_widget.children()[-3].toggle()
                self.prev_listwidgetitem_widget.children()[-3].setEnabled(True)
            if self.prev_listwidgetitem_widget.children()[-2].isChecked():
                self.prev_listwidgetitem_widget.children()[-2].toggle()
                self.prev_listwidgetitem_widget.children()[-2].setEnabled(True)
            if self.prev_listwidgetitem_widget.children()[-1].isChecked() \
            and self.selected_exercises_dict[int(self.prev_listwidgetitem_widget.children()[1].text())]["SolutionPath"] is not None \
            and self.selected_exercises_dict[int(self.prev_listwidgetitem_widget.children()[1].text())]["SolutionPath"] != "":
                self.prev_listwidgetitem_widget.children()[-1].toggle()
                self.prev_listwidgetitem_widget.children()[-1].setEnabled(True)
        if self.prev_listwidgetitem_widget is not None and listwidgetitem_widget.children()[1].text() == self.prev_listwidgetitem_widget.children()[1].text():
            if type != "Unmasked" and self.prev_listwidgetitem_widget.children()[-3].isChecked():
                self.prev_listwidgetitem_widget.children()[-3].toggle()
                self.prev_listwidgetitem_widget.children()[-3].setEnabled(True)
            if type != "Masked" and self.prev_listwidgetitem_widget.children()[-2].isChecked():
                self.prev_listwidgetitem_widget.children()[-2].toggle()
                self.prev_listwidgetitem_widget.children()[-2].setEnabled(True)
            if type != "Solution" and self.prev_listwidgetitem_widget.children()[-1].isChecked() \
            and self.selected_exercises_dict[int(self.prev_listwidgetitem_widget.children()[1].text())]["SolutionPath"] is not None \
            and self.selected_exercises_dict[int(self.prev_listwidgetitem_widget.children()[1].text())]["SolutionPath"] != "":
                self.prev_listwidgetitem_widget.children()[-1].toggle()
                self.prev_listwidgetitem_widget.children()[-1].setEnabled(True)
        qpixmap = QPixmap(png_path)
        if qpixmap.size().width() > self.png_label.size().width():
            qpixmap = qpixmap.scaled(self.png_label.size().width(), qpixmap.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.png_label.setPixmap(qpixmap)
        self.png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.png_label)
        # if self.IMAGE_TYPE == "Exercises":
        #     if self.masked_unmasked_button_layout.count() == 0:
        #         self.addExerciseImageButtons()

    def clearExerciseImageButtonsLayout(self):
        self.disconnectWidget(self.button_u)
        self.disconnectWidget(self.button_m)
        for i in reversed(range(self.masked_unmasked_button_layout.count())):
            self.masked_unmasked_button_layout.itemAt(i).widget().setParent(None)

    def showMaskedOrUnmasked(self):
        if self.button_u.isChecked() and self.button_u.isEnabled() is False:
            self.button_u.setEnabled(True)
            self.button_u.toggle()
            self.button_u.setCursor(QCursor(Qt.PointingHandCursor))

            self.button_m.setEnabled(False)
            self.button_m.setCursor(QCursor(Qt.ArrowCursor))

            np_image_array = np.array(self.images_in_grid[self.selected_extracted_image_entry_index]["masked"])

        elif self.button_m.isChecked() and self.button_m.isEnabled() is False:
            self.button_m.setEnabled(True)
            self.button_m.toggle()
            self.button_m.setCursor(QCursor(Qt.PointingHandCursor))

            self.button_u.setEnabled(False)
            self.button_u.setCursor(QCursor(Qt.ArrowCursor))

            np_image_array = np.array(self.images_in_grid[self.selected_extracted_image_entry_index]["unmasked"])


        height, width, channel = np_image_array.shape
        bytesPerLine = channel * width
        qImg = QImage(np_image_array, width, height, bytesPerLine, QImage.Format_RGBX8888)
        qpixmap = QPixmap(qImg)
        if qpixmap.size().width() > self.png_label.size().width():
            qpixmap = qpixmap.scaled(self.png_label.size().width(), qpixmap.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

        self.png_label.clear()
        self.png_label.setPixmap(qpixmap)
        self.png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.png_label)



    def addExerciseImageButtons(self):
        self.button_u = QPushButton("Unmasked")
        #button_u.setFlat(True)
        self.button_u.setFixedHeight(25)
        self.button_u.setStyleSheet("color: black")
        self.button_u.setCursor(QCursor(Qt.ArrowCursor))
        self.button_u.setCheckable(True)
        self.button_u.toggle()
        self.button_u.setEnabled(False)
        self.button_u.clicked.connect(lambda: self.showMaskedOrUnmasked())
        # frame_u = QFrame()
        # frame_u.setStyleSheet("background-color: white;")
        # frame_u_layout = QHBoxLayout()
        # frame_u_layout.setContentsMargins(0, 0, 0, 0)
        # frame_u_layout.addWidget(button_u)
        # frame_u.setLayout(frame_u_layout)
        # ElementStyles.regularShadow(frame_u)
        self.masked_unmasked_button_layout.addWidget(self.button_u)

        self.button_m = QPushButton("Masked")
        #button_m.setFlat(True)
        self.button_m.setFixedHeight(25)
        self.button_m.setStyleSheet("color: black")
        self.button_m.setCursor(QCursor(Qt.PointingHandCursor))
        self.button_m.setCheckable(True)
        self.button_m.clicked.connect(lambda: self.showMaskedOrUnmasked())
        # frame_m = QFrame()
        # frame_m.setStyleSheet("background-color: white;")
        # frame_m_layout = QHBoxLayout()
        # frame_m_layout.setContentsMargins(0, 0, 0, 0)
        # frame_m_layout.addWidget(button_m)
        # frame_m.setLayout(frame_m_layout)
        # ElementStyles.regularShadow(frame_m)
        self.masked_unmasked_button_layout.addWidget(self.button_m)



    def extractedImageEntryClicked(self, widget):
        self.selected_extracted_image_entry_index = int(widget.children()[2].text().split(" ")[-1])
        image_array = self.images_in_grid[self.selected_extracted_image_entry_index]
        if self.IMAGE_TYPE == "Exercises":
            if self.masked_unmasked_button_layout.count() == 0:
                self.addExerciseImageButtons()
            np_image_array = np.array(image_array["unmasked"])

        elif self.IMAGE_TYPE == "Solutions":
            np_image_array = np.array(image_array)

        height, width, channel = np_image_array.shape
        bytesPerLine = channel * width
        qImg = QImage(np_image_array, width, height, bytesPerLine, QImage.Format_RGBX8888)
        qpixmap = QPixmap(qImg)
        if qpixmap.size().width() > self.png_label.size().width():
            qpixmap = qpixmap.scaled(self.png_label.size().width(), qpixmap.size().height(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

        self.png_label.setPixmap(qpixmap)
        self.png_label.setWindowFlags(Qt.FramelessWindowHint)
        self.png_label.setAttribute(Qt.WA_TranslucentBackground)
        ElementStyles.regularShadow(self.png_label)

        ElementStyles.selectedListItem(widget)
        if self.prev_selected_extracted_image_widget is not None:
            ElementStyles.unselectedListItem(self.prev_selected_extracted_image_widget)
        self.prev_selected_extracted_image_widget = widget

    def deleteImageEntry(self):
        if self.prev_selected_extracted_image_widget is not None:
            self.images_in_grid.pop(self.selected_extracted_image_entry_index)
            self.extracted_image_arrays.pop(self.selected_extracted_image_entry_index)
            self.last_grid_row_idx = 0
            self.grid_col_start_idx = 0
            del_index = self.extracted_images_gridlayout.indexOf(self.prev_selected_extracted_image_widget)
            self.extracted_images_gridlayout.itemAt(del_index).widget().setParent(None)
            self.updateExtractedImagesGrid()
            self.selected_extracted_image_entry_index = None
            self.prev_selected_extracted_image_widget = None
            self.png_label.clear()





    def annotateAndExtract(self, chapter, section):
        if chapter.isdigit():
            if int(chapter) < 10:
                chapter = "0" + str(chapter)
            else:
                chapter = str(chapter)
        else:
            chapter = str(chapter)
        if section.isdigit():
            if int(section) != 0:
                if int(section) < 10:
                    section = "0" + str(section)
                else:
                    section = str(section)
            else:
                section = "00"
        else:
            section = str(section)
        self.current_set = {}
        if self.IMAGE_TYPE == "Exercises":
            set_dir_masked = os.path.join(self.e_packs_txtbk_dir, "Exercises Images", "Masked", chapter)
            set_dir_unmasked = os.path.join(self.e_packs_txtbk_dir, "Exercises Images", "Unmasked", chapter)
            os.makedirs(set_dir_masked, exist_ok=True)
            os.makedirs(set_dir_unmasked, exist_ok=True)
            self.current_set = {"Chapter": chapter, "Section": section, "Images_Dir": {"Masked": set_dir_masked, "Unmasked": set_dir_unmasked}}
        elif self.IMAGE_TYPE == "Solutions":
            set_dir = os.path.join(self.e_packs_txtbk_dir, "Solutions Images", chapter)
            os.makedirs(set_dir, exist_ok=True)
            self.current_set = {"Chapter": chapter, "Section": section, "Images_Dir": set_dir}
        if len(self.event_handlers) > 0:
            for i in range(len(self.event_handlers)):
                self.event_handlers[i].disconnect()
        for i in range(len(Config.STANDARD_OPs)):
            command = Config.STANDARD_OPs[i]
            if len(self.event_handlers) != len(Config.ALL_OPs):
                self.event_handlers.append(QShortcut(QKeySequence(command), self))
            self.event_handlers[i].activated.connect(partial(self.image_extractor.annotateOneColumn, command, self.current_set, self.ret_current_index_number, self.IMAGE_TYPE))
        if len(self.event_handlers) != len(Config.ALL_OPs):
            self.event_handlers.append(QShortcut(QKeySequence(Config.OP_TWO_COLUMNS), self))
            self.event_handlers.append(QShortcut(QKeySequence(Config.OP_RESET_IMAGE_LIST), self))
        self.event_handlers[-2].activated.connect(partial(self.image_extractor.annotateTwoColumns, Config.OP_TWO_COLUMNS, self.current_set, self.ret_current_index_number, self.IMAGE_TYPE))
        self.event_handlers[-1].activated.connect(partial(self.saveAndUploadExtractedImages))
        print("Current set: " + self.current_set["Chapter"] + "." + self.current_set["Section"])
        print("Extraction Mode: " + self.IMAGE_TYPE)
        print("Shortcuts active")
        print("------------------------------------------")


    def ret_current_index_number(self):
        #temp_files = os.listdir(Config.TEMP_SS_PATH)
        if len(self.extracted_image_arrays) > 0:
            if self.IMAGE_TYPE == "Exercises":
                return list(self.extracted_image_arrays.keys())[-1]
            else:
                return list(self.extracted_image_arrays.keys())[-1]
        elif len(self.selected_exercises) > 0 and not self.overwrite_image_checkbox.isChecked() and self.default_starting_index_spinbox.value() == -1:
            if self.IMAGE_TYPE == "Exercises":
                return self.selected_exercises[-1]["ExerciseNumber"]
            else:
                return self.selected_exercises[0]["ExerciseNumber"] - self.default_idx_inc_spinbox.value()
        elif self.dnr_index_checkbox.isChecked() and self.selected_chap_num == self.current_chap_num:
            return self.last_image_index
        elif self.dnr_index_checkbox.isChecked() and self.selected_chap_num != self.current_chap_num:
            self.current_chap_num = self.selected_chap_num
            return 0
        else:
            return self.default_starting_index_spinbox.value() - self.default_idx_inc_spinbox.value()


    def saveAndUploadExtractedImages(self):
        self.extracted_images_timer.disconnect()
        eids = [entry["ExerciseID"] for entry in self.selected_exercises]
        if self.IMAGE_TYPE == "Exercises":
            for image_index, array in zip(self.extracted_image_arrays.keys(), self.extracted_image_arrays.values()):
                masked_image_name = self.setImageName(self.current_set, image_index, "masked")
                m_exercise_path = os.path.join(self.current_set["Images_Dir"]["Masked"], masked_image_name)
                array["masked"].save(m_exercise_path)
                m_exercise_rel_path = " -- ".join(m_exercise_path.split("Exercise Packs\\")[-1].split("\\"))

                unmasked_image_name = self.setImageName(self.current_set, image_index, "unmasked")
                u_exercise_path = os.path.join(self.current_set["Images_Dir"]["Unmasked"], unmasked_image_name)
                array["unmasked"].save(u_exercise_path)
                u_exercise_rel_path = " -- ".join(u_exercise_path.split("Exercise Packs\\")[-1].split("\\"))

                eid = ".".join(masked_image_name.split(".")[:-2])
                EN = int(masked_image_name.split(".")[2])
                add_row = (self.selected_textbook_ID, eid, self.selected_chap_num, self.selected_sect_num, EN, None, str(False), 0, None, None, None, None, None, u_exercise_rel_path, m_exercise_rel_path, None)
                if eid not in eids:
                    self.db_interface.insertEntry("New Exercise", add_row)
                    print("Inserted row: " + str(add_row))
                else:
                    print("Row already exists: " + str(add_row))
                self.last_image_index = image_index
        elif self.IMAGE_TYPE == "Solutions":
            exercise_numbers = [entry["ExerciseNumber"] for entry in self.selected_exercises]
            sol_exists_vals = [eval(entry["SolutionExists"]) if (entry["SolutionExists"] != None and entry["SolutionExists"] != "") else entry["SolutionExists"] for entry in self.selected_exercises]
            for eid, EN, sol_exists in zip(eids, exercise_numbers, sol_exists_vals):
                if EN in self.extracted_image_arrays.keys():
                    if self.overwrite_image_checkbox.isChecked() or sol_exists == False or sol_exists == None or sol_exists == "":
                        image_name = self.setImageName(self.current_set, EN, None)
                        solution_path = os.path.join(self.current_set["Images_Dir"], image_name)
                        self.extracted_image_arrays[EN].save(solution_path)
                        solution_rel_path = " -- ".join(solution_path.split("Exercise Packs\\")[-1].split("\\"))
                        update_row = [str(True), solution_rel_path, self.selected_textbook_ID, eid]
                        self.db_interface.updateEntry("Solution Path For Exercise", update_row)
                        print("Updated row: " + str(update_row))
                    elif (not self.overwrite_image_checkbox.isChecked() and sol_exists != None and sol_exists != "") or sol_exists == True:
                        print("Solution already exist or overwrite is false: " + str(EN))
                    self.last_image_index = EN
                elif sol_exists is None or sol_exists == "":
                    update_row = [str(False), "", self.selected_textbook_ID, eid]
                    self.db_interface.updateEntry("Solution Path For Exercise", update_row)
                    print("Updated row: " + str(update_row))
        if self.IMAGE_TYPE == "Exercises":
            update_row = [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num]
            self.db_interface.updateEntry("AllExercisesExtracted", update_row)
        elif self.IMAGE_TYPE == "Solutions":
            update_row = [self.selected_textbook_ID, self.selected_chap_num, self.selected_sect_num]
            self.db_interface.updateEntry("AllSolutionsExtracted", update_row)
        print("------------------------------------------")
        #self.current_set_index += 1
        self.extracted_image_arrays.clear()
        self.images_in_grid.clear()
        self.clearImagesGrid()
        self.image_extractor.header = []
        self.clearExerciseImageButtonsLayout()
        if self.current_set_index + 1 < len(self.textbook_sections):
            self.prev_selected_extracted_image_widget = None
            self.sectionsEntryClicked(self.current_set_index + 1)
            self.extracted_images_timer.start(1000)
            self.extracted_images_timer.timeout.connect(lambda: self.updateExtractedImagesGrid())
            #print("Current set: " + str(self.selected_chap_num) + " " + str(self.selected_sect_num))
            print(self.IMAGE_TYPE + " sets left: " + str(len(self.textbook_sections) - self.current_set_index))#self.current_set_index incremented
            print("------------------------------------------")
        else:
            print("Finished.")
            print("------------------------------------------")

    def setImageName(self, current_set, index, mask_type):
        if self.IMAGE_TYPE == "Exercises":
            if mask_type == "masked":
                image_type = "M"
            elif mask_type == "unmasked":
                image_type = "U"
        elif self.IMAGE_TYPE == "Solutions":
            image_type = "S"
        if current_set["Section"] == '00':
            image_name = ".".join([str(current_set["Chapter"]), "00", str(index).zfill(3), image_type, "png"])
        else:
            image_name = ".".join([current_set["Chapter"], current_set["Section"], str(index).zfill(3), image_type, "png"])
        return image_name