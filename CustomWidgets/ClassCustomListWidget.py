import ElementStyles
from PyQt5.QtWidgets import QScrollBar, QHBoxLayout, QLabel, QWidget, QListWidgetItem, QFrame, QPushButton, QCheckBox, QLineEdit, QVBoxLayout
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QListWidget, QListView, QSizePolicy, QAbstractScrollArea
from PyQt5.QtGui import QPixmap, QColor, QIcon, QImage, QCursor, QPainter
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice,Qt, QObject, QSize
from PyQt5 import QtCore
import cv2
import numpy as np
import io
from PIL import Image
import Config

class CustomListWidget(QListWidget):
    list_widget = None
    scroll_bar = None
    list_name = None
    study_list_page = None



    def __init__(self, *args, **kwargs):
        super(CustomListWidget, self).__init__(*args, **kwargs)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


    def mousePressEvent(self, event):
        try:
            self.study_list_page.sl_moved = self.itemWidget(self.itemAt(event.pos())).children()[5].text()
        except:
            pass
        #print(self.study_list_page.sl_moved)
        super().mousePressEvent(event)

    def dropEvent(self, event):
        new_sl_collection_name = self.parent().children()[1].children()[2].text()
        if self.study_list_page.sl_moved not in [study_list["StudyListName"] for study_list in self.study_list_page.sl_collections_dict[new_sl_collection_name].values()]:
            old_sl_collection_name = [study_list_coll_name for study_list_coll_name in self.study_list_page.sl_collections_dict if self.study_list_page.sl_moved in self.study_list_page.sl_collections_dict[study_list_coll_name].keys()][0]
            self.study_list_page.sl_collections_dict[new_sl_collection_name][self.study_list_page.sl_moved] = self.study_list_page.sl_collections_dict[old_sl_collection_name].pop(self.study_list_page.sl_moved)
            # Updating db
            sl_moved_id = next(item for item in self.study_list_page.study_lists if item["StudyListName"] == self.study_list_page.sl_moved)["StudyListID"]

            new_sl_collection = next(item for item in self.study_list_page.study_list_collections if item["CollectionName"] == new_sl_collection_name)
            if new_sl_collection["Tags"] is not None:
                new_sl_coll_tags = new_sl_collection["Tags"].split(",")
            else:
                new_sl_coll_tags = []
            if sl_moved_id not in new_sl_coll_tags:
                new_sl_coll_tags.append(sl_moved_id)
                new_sl_collection["Tags"] = ",".join(new_sl_coll_tags)
                update_list = [new_sl_collection["Tags"], new_sl_collection["CollectionID"]]
                self.study_list_page.db_interface.updateEntry("Update SL Collection Tags", update_list)

            old_sl_collection = next(item for item in self.study_list_page.study_list_collections if item["CollectionName"] == old_sl_collection_name)
            old_sl_coll_tags = old_sl_collection["Tags"].split(",")
            old_sl_coll_tags.pop(old_sl_coll_tags.index(sl_moved_id))
            if old_sl_coll_tags is not None:
                old_sl_collection["Tags"] = ",".join(old_sl_coll_tags)
            else:
                old_sl_collection["Tags"] = None
            update_list = [old_sl_collection["Tags"],  old_sl_collection["CollectionID"]]
            self.study_list_page.db_interface.updateEntry("Update SL Collection Tags", update_list)

            self.study_list_page.updateSlCollectionList()
        self.study_list_page.sl_moved = None



    def setList(self, query_table_name: str, query_entries: list, give_shadow=True, vertical_spacing=3) -> None:
        self.clear()
        self.list_name = query_table_name
        self.give_shadow = give_shadow
        self.vertical_spacing = vertical_spacing
        for entry in query_entries:
            listitem = self.createWidget(query_table_name, entry)
            self.insert(listitem)
        self.setSpacing(self.vertical_spacing)
        self.scroll_bar = QScrollBar()
        self.scroll_bar.setStyleSheet("background : white;")
        self.setVerticalScrollBar(self.scroll_bar)



    def insert(self, listitem: QWidget) -> None:
        item = QListWidgetItem(self)
        #item.setBackground(QColor('#eeeeec'))
        item.setSizeHint(listitem.sizeHint())
        item.setText(str(self.count()))
        self.setItemWidget(item, listitem)


    def createWidget(self, query_table_name: str, entry) -> QWidget:
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

        elif query_table_name == "Study Lists":
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

        elif query_table_name == "Selected Study List Sections":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            checkbox = QCheckBox()
            checkbox.setFixedWidth(13)
            elementLayout.addWidget(checkbox)

            label = QLabel()
            label.setText("")
            label.setFixedWidth(25)
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["TextbookID"])
            label.setFixedWidth(50)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["ChapterNumber"])
            label.setFixedWidth(50)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["SectionNumber"])
            label.setFixedWidth(50)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(str(entry["Count"]))
            label.setFixedWidth(32)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            progress_label = QLabel()
            self.updateProgressBar(progress_label, entry)
            elementLayout.addWidget(progress_label)

            button = QPushButton("Start")
            button.setStyleSheet("background-color: rgb(0, 170, 127); color: white")
            elementLayout.addWidget(button)
            button.setFixedWidth(50)

            label = QLabel()
            label.setText("")
            label.setFixedWidth(70)
            elementLayout.addWidget(label)

            # label = QLabel()
            # label.setText("")
            # label.setFixedWidth(20)
            # elementLayout.addWidget(label)

            # button = QPushButton("Remove")
            # button.setStyleSheet("background-color: rgb(255, 76, 17); color: white")
            # elementLayout.addWidget(button)
            # button.setFixedWidth(50)

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
            checkbox = QCheckBox()
            checkbox.setFixedWidth(13)
            elementLayout.addWidget(checkbox)

            label = QLabel()
            label.setText("")
            label.setFixedWidth(25)
            elementLayout.addWidget(label)

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
            label.setText(str(entry["Count"]))
            label.setFixedWidth(32)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            progress_label = QLabel()
            self.updateProgressBar(progress_label, entry)
            elementLayout.addWidget(progress_label)

            button = QPushButton("Start")
            button.setStyleSheet("background-color: rgb(0, 170, 127); color: white")
            ElementStyles.lightShadow(button)
            elementLayout.addWidget(button)
            button.setFixedWidth(50)

            label = QLabel()
            label.setText("")
            label.setFixedWidth(20)
            elementLayout.addWidget(label)

            add_to_sl_button = QPushButton("Add to a Study List")
            add_to_sl_button.setStyleSheet("background-color: #2A4D87; color: white")
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

        elif query_table_name == "Flashcard Categories":
            elementLayout.setContentsMargins(5, 5, 5, 5)

            label = QLabel()
            label.setText(entry)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

        elif query_table_name == "Flashcard Textbooks":
            elementLayout.setContentsMargins(5, 5, 5, 5)

            label = QLabel()
            label.setText(entry["Authors"])
            label.setFixedWidth(60)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["Title"])
            label.setFixedWidth(290)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

            label = QLabel()
            label.setText(entry["Edition"])
            #label.setFixedWidth(300)
            label.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(label)

        elif query_table_name == "Flashcard Sets":
            elementLayout.setContentsMargins(5, 5, 5, 5)
            checkbox = QCheckBox()
            checkbox.setFixedWidth(13)
            elementLayout.addWidget(checkbox)

            label = QLabel()
            label.setText("")
            label.setFixedWidth(25)
            elementLayout.addWidget(label)

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

        # elif query_table_name == "Study List Collections":
        #     elementLayout.setContentsMargins(0, 0, 0, 0)
        #
        #     vboxLayout = QVBoxLayout()
        #     vboxLayout.setSpacing(0)
        #     vboxLayout.setContentsMargins(0, 0, 0, 0)
        #
        #     hboxLayout = QHBoxLayout()
        #     hboxLayout.setContentsMargins(5, 5, 5, 5)
        #
        #     label = QLabel()
        #     pix = QPixmap(Config.RIGHT_ARROW)
        #     pix = pix.scaled(15, 15, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        #     label.setPixmap(pix)
        #     label.setFixedWidth(25)
        #     hboxLayout.addWidget(label)
        #
        #     #label.setFixedHeight(23)
        #
        #     label = QLabel()
        #     label.setText(entry["CollectionName"])
        #     label.setFixedWidth(350)
        #     label.setStyleSheet("color: #4e5256")
        #     hboxLayout.addWidget(label)
        #
        #     label.setFixedHeight(33)
        #
        #
        #     label = QLabel()
        #     label.setText("")
        #     label.setFixedWidth(25)
        #     hboxLayout.addWidget(label)
        #
        #     label = QLabel()
        #     label.setText(str(len(entry["Tags"].split(","))))
        #     label.setStyleSheet("color: #4e5256")
        #     hboxLayout.addWidget(label)
        #
        #     widget = QWidget()
        #     widget.setLayout(hboxLayout)
        #     widget.setFixedHeight(33)
        #     # children = widget.children()
        #     # for i in range(1, len(children)):
        #     #     children[i].setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #     #     children[i].setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #     vboxLayout.addWidget(widget)
        #
        #     widget = QWidget()
        #     widget.setLayout(vboxLayout)
        #     elementLayout.addWidget(widget)

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

        # def clear(self) -> None:
        #     self.clear()

        # def itemWidget(self, list_widget_item: QListWidgetItem) -> QWidget:
        #     return self.itemWidget(list_widget_item)

        # def item(self, index: int) -> QListWidgetItem:
        #     return self.item(index)

        # def removeRow(self, i: int) -> None:
        #     self.removeRow(i)

        # def connect(self, function) -> None:
        #     self.itemClicked.connect(lambda: function)

        # def row(self, item_widget: QListWidgetItem) -> int:
        #     return self.row(item_widget)

        # def insertListIntoWidget(self, query_table_name: str, query_entries: list, top_list_item: QListWidgetItem) -> None:

        # def insertListIntoWidget(self, query_table_name: str, query_entries: list, top_list_item: QListWidgetItem) -> None:
        #     sublist_widget = QListWidget
        #     old_count = self.count()
        #     for i in range(len(query_entries)):
        #         item = QListWidgetItem(self)
        #         item.setSizeHint(self.itemWidget(top_list_item).sizeHint())
        #         self.insertItem(self.count(), item)
        #     new_count = self.count()
        #     if self.row(top_list_item) != old_count - 1:
        #         j = old_count - 1
        #         for i in reversed(range(self.row(top_list_item) + 1, new_count)):
        #             listitem = self.itemWidget(self.item(j))
        #             item = self.item(j).clone()
        #             item.setSizeHint(self.itemWidget(top_list_item).sizeHint())
        #             self.insertItem(i + 1, item)
        #             self.setItemWidget(item, listitem)
        #             self.takeItem(j)
        #             j -= 1
        #             if j == self.row(top_list_item):
        #                 break
        #     j = self.row(top_list_item) + 1
        #     for entry in query_entries:
        #         listitem = self.createWidget("Study List", entry, giveShadow=False)
        #         #self.item(j).setSizeHint(listitem.sizeHint())
        #         self.setItemWidget(self.item(j), listitem)
        #         j += 1
        #     #break
        #     pass
        #     pass

        # def removeFromList(self, query_table_name: str, query_entries: list, top_list_item: QListWidgetItem) -> None:
        #     old_count = self.count()
        #     i = self.row(top_list_item) + 1
        #     j = self.row(top_list_item) + 1
        #     while len(self.itemWidget(self.item(i)).children()) != len(self.itemWidget(top_list_item).children()):
        #         self.takeItem(i)
        #         j += 1
        #         if j == old_count:
        #             break

        # .setDragDropMode(QAbstractItemView.InternalMove)
        # def activateDragDropMode(self):
        #     self.setDragDropMode(QAbstractItemView.DragDrop)
        #     self.setAcceptDrops(True)

        # def dragEnterEvent(self, event):
        #     self.study_list_page.sl_moved = None
        #     super().dragEnterEvent(event)

        # def dragMoveEvent(self, event):
        #     if self.study_list_page.sl_moved == None:
        #         self.study_list_page.sl_moved = self.itemWidget(self.itemAt(event.pos())).children()[5].text()
        #         print(self.study_list_page.sl_moved)
        #         pass
        #         pass
