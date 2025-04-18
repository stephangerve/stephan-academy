from PyQt5 import uic
import ElementStyles
from ContentPages.ClassPage import Page
from CustomWidgets.ClassScrollAreaWidget import ScrollAreaWidget
from CustomWidgets.ClassCustomListWidget import CustomListWidget
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QAbstractItemView
from PyQt5.QtGui import QFont, QCursor, QPixmap, QImage
from PyQt5.QtCore import Qt
import Config
import random
import string
from datetime import date
import matplotlib.pyplot as plt
import io
import os
import numpy as np
from datetime import datetime


class StudyListPage(Page):

    def __init__(self, content_pages):
        Page.__init__(self, Config.StudyListPage_page_number)
        uic.loadUi('Resources/UI/study_list_page.ui', self)
        self.content_pages = content_pages
        self.sl_scroll_area_element = ScrollAreaWidget(self.sl_collection_scrollarea)
        self.sect_grades_counts = {}
        self.remove_sections_from_sl_button = None
        self.TID_sort_order = None
        self.CN_sort_order = None
        self.SN_sort_order = None
        self.count_sort_order = None
        self.progress_sort_order = None
        self.sl_moved = None

    def objectReferences(self, db_interface, practice_page):
        self.db_interface = db_interface
        self.practice_page = practice_page


    def showPage(self):
        self.selected_study_list = None
        self.selected_section = None
        self.prev_study_list_item_widget = None
        self.prev_section_list_widget_item = None
        self.sl_date_filter_button.clicked.connect(lambda: self.setDateFilter())
        self.setDateFilter()
        #self.updateSLCollectionsDict()
        self.sections_selected_count = 0
        # if self.study_lists_listwidget.count() > 0:
        #     self.study_lists_listwidget.itemClicked.disconnect()
        if self.sl_sections_listwidget.count() > 0:
            self.disconnectWidget(self.sl_sections_listwidget)
        self.progress_donut_label.clear()
        self.sb_frame.setStyleSheet("background-color: gray")
        self.start_button_2.setStyleSheet("color: black")
        self.start_button_2.setEnabled(False)

        ElementStyles.regularShadow(self.remove_from_sl_button)
        ElementStyles.regularShadow(self.textbook_info_frame_left_2)
        ElementStyles.regularShadow(self.ex_stats_info_2)
        ElementStyles.regularShadow(self.sb_frame)
        ElementStyles.lightShadow(self.start_button_2)
        ElementStyles.lightShadow(self.mode_frame_2)
        ElementStyles.lightShadow(self.grade_filter_frame_2)
        self.clearExercisesGrid()
        self.sl_sections_listwidget.clear()
        self.sl_scroll_area_element.setList("Study List Collections", self.study_list_collections)



        self.selected_collection = None
        self.selected_study_list = None
        self.selected_section = None
        self.add_new_sl_button.clicked.connect(lambda: self.addNewStudyList())
        self.create_new_coll_button.clicked.connect(lambda: self.createNewSLCollection())
        self.content_pages.setCurrentIndex(self.page_number)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            sl_coll_names = [sl["CollectionName"] for sl in self.study_list_collections]
            childWidget = self.childAt(event.pos())
            while True:
                if childWidget is not None:
                    if len(childWidget.children()) == 5:
                        if type(childWidget.children()[2]) == QLabel:
                            if childWidget.children()[2].text() in sl_coll_names:
                                self.slCollectionClicked(childWidget.children()[2].text(), childWidget.parent())
                    childWidget = childWidget.parent()
                else:
                    break


    def updateSLCollectionsDict(self):
        self.study_list_collections = self.db_interface.fetchEntries("Study List Collections", [])
        self.sl_collections_dict = dict.fromkeys([collection["CollectionName"] for collection in self.study_list_collections])
        self.sl_collection_expanded = dict(zip([collection["CollectionName"] for collection in self.study_list_collections], [False] * len(self.study_list_collections)))
        self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
        for cname in self.sl_collections_dict:
            slc_tags_list = [coll["Tags"] for coll in self.study_list_collections if coll["CollectionName"] == cname and coll["Tags"] != None and coll["Tags"] != "None"]
            slc_tags = []
            if len(slc_tags_list) > 0:
                slc_tags = slc_tags_list[0].split(",")
            study_list_names = [study_list["StudyListName"] for study_list in self.study_lists if study_list["StudyListID"] in slc_tags]
            self.sl_collections_dict[cname] = dict.fromkeys(study_list_names)
            for sl_name in study_list_names:
                self.sl_collections_dict[cname][sl_name] = {"StudyListName": sl_name, "Count": 0, "NumExercisesA": 0, "NumExercisesB": 0, "NumExercisesC": 0, "NumExercisesD": 0, "NumExercisesF": 0, "NoGrade": 0, "Sections": []}

        all_sl_exercises = self.db_interface.fetchEntries("All Study List Exercises", [])
        for ex in all_sl_exercises:
            ex_tags = ex["Tags"].split(",")
            for ex_tag in ex_tags:
                cnames = [collection["CollectionName"] for collection in self.study_list_collections if collection["Tags"] != None and ex_tag in collection["Tags"].split(",")]
                sl_name = [study_list["StudyListName"] for study_list in self.study_lists if ex_tag == study_list["StudyListID"]][0]
                for cname in cnames:
                    section = [sect for sect in self.sl_collections_dict[cname][sl_name]["Sections"] if sect["TextbookID"] == ex["TextbookID"] and sect["ChapterNumber"] == ex["ChapterNumber"] and sect["SectionNumber"] == ex["SectionNumber"]]
                    if len(section) == 0:
                        section_dict = {"TextbookID": ex["TextbookID"], "ChapterNumber": ex["ChapterNumber"], "SectionNumber": ex["SectionNumber"]}
                        section_dict["NumExercisesA"] = 0
                        section_dict["NumExercisesB"] = 0
                        section_dict["NumExercisesC"] = 0
                        section_dict["NumExercisesD"] = 0
                        section_dict["NumExercisesF"] = 0
                        section_dict["NoGrade"] = 0
                        section_dict["Exercises"] = []
                        section_dict["Count"] = 0
                        self.sl_collections_dict[cname][sl_name]["Sections"].append(section_dict)
                    else:
                        section_dict = section[0]
                    if ex["Attempts"] > 0:
                        if datetime.strptime(ex["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
                            if ex["Grade"] == 'A':
                                section_dict["NumExercisesA"] += 1
                                self.sl_collections_dict[cname][sl_name]["NumExercisesA"] += 1
                            elif ex["Grade"] == 'B':
                                section_dict["NumExercisesB"] += 1
                                self.sl_collections_dict[cname][sl_name]["NumExercisesB"] += 1
                            elif ex["Grade"] == 'C':
                                section_dict["NumExercisesC"] += 1
                                self.sl_collections_dict[cname][sl_name]["NumExercisesC"] += 1
                            elif ex["Grade"] == 'D':
                                section_dict["NumExercisesD"] += 1
                                self.sl_collections_dict[cname][sl_name]["NumExercisesD"] += 1
                            elif ex["Grade"] == 'F':
                                section_dict["NumExercisesF"] += 1
                                self.sl_collections_dict[cname][sl_name]["NumExercisesF"] += 1
                        else:
                            section_dict["NoGrade"] += 1
                            self.sl_collections_dict[cname][sl_name]["NoGrade"] += 1
                    elif ex["SolutionExists"] == 'True':
                        section_dict["NoGrade"] += 1
                        self.sl_collections_dict[cname][sl_name]["NoGrade"] += 1

                    section_dict["Exercises"].append(ex)
                    section_dict["Count"] += 1
                    self.sl_collections_dict[cname][sl_name]["Count"] += 1
        for cname in self.sl_collections_dict:
            for sl_name in self.sl_collections_dict[cname]:
                self.sl_collections_dict[cname][sl_name]["Sections"] = sorted(self.sl_collections_dict[cname][sl_name]["Sections"], key=lambda x: (int(x["ChapterNumber"]) if x["ChapterNumber"].isdigit() else 999, int(x["SectionNumber"]) if x["SectionNumber"].isdigit() else 999))


    def setDateFilter(self):
        parsed_date = [str(l).zfill(2) if len(str(l)) == 1 else str(l) for l in list(self.sl_date_filter_edit.date().getDate())]
        self.date_filter = "/".join([parsed_date[1], parsed_date[2], parsed_date[0]])
        self.updateSLCollectionsDict()
        if self.prev_study_list_item_widget is not None:
            self.studyListClicked(self.prev_study_list_item_widget)


    def showProgressDonut(self):
        if len(self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"]) > 0:
            study_list = self.sl_collections_dict[self.selected_collection][self.selected_study_list]
            section_grades = [study_list["NumExercisesA"], study_list["NumExercisesB"], study_list["NumExercisesC"], study_list["NumExercisesD"], study_list["NumExercisesF"], study_list["NoGrade"]]
            grades_dict = dict(zip(['A', 'B', 'C', 'D', 'F', 'NG'], section_grades))
            # grades_dict = dict(zip(['A', 'B', 'C', 'D', 'F', 'NG'], [0] * 6))
            # for section in self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"]:
            #     for exercise in section["Exercises"]:
            #         if exercise["Grade"] in list(grades_dict.keys()) and datetime.strptime(exercise["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
            #             grades_dict[exercise["Grade"]] += 1
            #         else:
            #             grades_dict["NG"] += 1
            plt.figure().clear()
            plt.pie(list(grades_dict.values()), colors=[tuple([val / 255 for val in color]) for color in list(Config.EXERCISE_GRADE_COLORS.values()) + [Config.GREY_LIGHT_BLUE]], radius=0.8)
            centre_circle = plt.Circle((0, 0), 0.6, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            buffer = io.BytesIO()
            fig.savefig(buffer, format='raw')
            plt.close(fig)
            buffer.seek(0)
            img_arr = np.reshape(np.frombuffer(buffer.getvalue(), dtype=np.uint8), newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
            buffer.close()
            height, width, channel = img_arr.shape
            bytesPerLine = channel * width
            qImg = QImage(img_arr, width, height, bytesPerLine, QImage.Format_RGBX8888)
            image_pixmap = QPixmap(qImg)
            self.progress_donut_label.clear()
            self.progress_donut_label.setPixmap(image_pixmap)
        else:
            self.progress_donut_label.clear()


    def slCollectionClicked(self, collection_name, item_widget):
        self.selected_collection = collection_name
        if self.prev_study_list_item_widget is not None:
            ElementStyles.unselectedListItem(self.prev_study_list_item_widget)
        self.prev_study_list_item_widget = None
        if self.sl_collection_expanded[self.selected_collection] is False:
            self.sl_collection_expanded[self.selected_collection] = True
            list_widget = CustomListWidget()
            list_widget.setSpacing(0)
            list_widget.setStyleSheet("border: None")
            list_widget.setDragDropMode(QAbstractItemView.DragDrop)
            list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            list_widget.setAcceptDrops(True)
            list_widget.setList("Study Lists", self.sl_collections_dict[self.selected_collection].values(), give_shadow=False, vertical_spacing=0)
            list_widget.study_list_page = self
            item_widget.children()[0].addWidget(list_widget)
            item_widget.parent().setFixedHeight(33 * (len(self.sl_collections_dict[self.selected_collection].values()) + 1))

            # if self.sl_collection_scrollarea.verticalScrollBar().isVisible():
            #     item_widget.children()[2].setFixedWidth(item_widget.width() - self.sl_collection_scrollarea.verticalScrollBar().width())
            # else:
            #     item_widget.children()[2].setFixedWidth(item_widget.width())
            if self.sl_collection_scrollarea.verticalScrollBar().isVisible():
                item_widget.children()[2].setFixedWidth(item_widget.width() - self.sl_collection_scrollarea.verticalScrollBar().width())
                for i in range(item_widget.children()[2].count()):
                    item_widget.children()[2].itemWidget(item_widget.children()[2].item(i)).setFixedWidth(item_widget.width() - self.sl_collection_scrollarea.verticalScrollBar().width())



            pix = QPixmap(Config.DOWN_ARROW)
            pix = pix.scaled(15, 15, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            item_widget.children()[1].children()[1].setPixmap(pix)
            
            item_widget.children()[2].itemClicked.connect(lambda: self.studyListClicked(item_widget.children()[2].itemWidget(item_widget.children()[2].currentItem())))


        else:
            self.sl_collection_expanded[self.selected_collection] = False
            self.disconnectWidget(item_widget.children()[2])
            #item_widget.children()[0].removeWidget(item_widget.children()[2])
            #item_widget.children()[2].setParent(None)
            if len(item_widget.children()) > 2:
                item_widget.children()[2].deleteLater()
            item_widget.parent().setFixedHeight(33)
            pix = QPixmap(Config.RIGHT_ARROW)
            pix = pix.scaled(15, 15, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            item_widget.children()[1].children()[1].setPixmap(pix)

    def updateSlCollectionList(self):
        for i in range(1, len(self.sl_collection_scrollarea.children()[0].children()[0].children())):
            scroll_area_widget = self.sl_collection_scrollarea.children()[0].children()[0].children()[i].children()[1]
            widget_sl_col_name = scroll_area_widget.children()[1].children()[2].text()
            if self.sl_collection_expanded[widget_sl_col_name]:
                self.slCollectionClicked(widget_sl_col_name, scroll_area_widget)
                self.slCollectionClicked(widget_sl_col_name, scroll_area_widget)
                scroll_area_widget.children()[1].children()[4].setText(str(len(list(self.sl_collections_dict[widget_sl_col_name].keys()))))


    def studyListClicked(self, item_widget):
        # pix = QPixmap(Config.DRAG_HANDLE)
        # pix = pix.scaled(15, 15, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        # item_widget.children()[1].setPixmap(pix)
        #self.study_lists_listwidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.TID_sort_order = None
        self.CN_sort_order = None
        self.SN_sort_order = None
        self.count_sort_order = None
        self.progress_sort_order = None
        self.prev_section_list_widget_item = None
        self.sb_frame.setStyleSheet("background-color: gray")
        self.start_button_2.setStyleSheet("color: black")
        self.start_button_2.setEnabled(False)
        self.sl_sections_listwidget.clear()
        self.chapter_info_label_2.clear()
        self.section_info_label_2.clear()
        self.clearExercisesGrid()
        old_study_list = self.selected_study_list
        self.selected_study_list = item_widget.children()[5].text()
        self.selected_collection = [coll for coll in self.sl_collections_dict if self.selected_study_list in self.sl_collections_dict[coll]][0]
        if len(self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"]) > 0:
            self.updateSLSectionList()
            self.showProgressDonut()
            self.sl_sections_listwidget.itemClicked.connect(lambda: self.studyListSectionClicked(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.currentItem())))
            for i in range(self.sl_sections_listwidget.count()):
                self.disconnectWidget(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[-2])
                self.disconnectWidget(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[1])
                self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[-2].clicked.connect(lambda state, i=i: self.startButtonClicked(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i))))
                self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[1].stateChanged.connect(lambda state, i=i: self.multipleSectionsSelected(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i))))
        else:
            self.progress_donut_label.clear()
        if self.prev_study_list_item_widget is not None:
            ElementStyles.unselectedListItem(self.prev_study_list_item_widget)
            progress_label = self.prev_study_list_item_widget.children()[7]
            #self.sl_sections_listwidget.updateProgressBar(progress_label, self.sl_collections_dict[self.selected_collection][old_study_list])
        ElementStyles.selectedListItem(item_widget)
        progress_label = item_widget.children()[7]
        self.sl_sections_listwidget.updateProgressBar(progress_label, self.sl_collections_dict[self.selected_collection][self.selected_study_list])
        self.prev_study_list_item_widget = item_widget
        self.sections_selected_count = 0
        self.disconnectWidget(self.sl_select_all_sections_checkbox)
        self.disconnectWidget(self.sl_CN_sort_button)
        self.disconnectWidget(self.sl_CN_sort_button)
        self.disconnectWidget(self.sl_SN_sort_button)
        self.disconnectWidget(self.sl_count_sort_button)
        self.disconnectWidget(self.sl_progress_sort_button)
        self.sl_select_all_sections_checkbox.stateChanged.connect(lambda: self.selectAllSections(self.sl_select_all_sections_checkbox.checkState()))
        self.sl_CN_sort_button.clicked.connect(lambda: self.sortSectionsListBy("ChapterNumber"))
        self.sl_SN_sort_button.clicked.connect(lambda: self.sortSectionsListBy("SectionNumber"))
        self.sl_count_sort_button.clicked.connect(lambda: self.sortSectionsListBy("Count"))
        self.sl_progress_sort_button.clicked.connect(lambda: self.sortSectionsListBy("Progress"))

    def startButtonClicked(self, item_widget):
        self.selected_section = [sect for sect in self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"] if sect["TextbookID"] == item_widget.children()[3].text() and sect["ChapterNumber"] == item_widget.children()[4].text() and sect["SectionNumber"] == item_widget.children()[5].text()][0]
        exercises = self.selected_section["Exercises"]
        num = int(exercises[0]["ExerciseID"].split(".")[-1])
        self.practice_page.showPage(num, exercises)

    def selectAllSections(self, state):
        for i in range(self.sl_sections_listwidget.count()):
            item_widget = self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i))
            self.disconnectWidget(item_widget.children()[1])
            if state:
                if not item_widget.children()[1].isChecked():
                    item_widget.children()[1].setChecked(True)
                    self.sections_selected_count += 1
                    ElementStyles.highlightListItem(item_widget)
            else:
                if item_widget.children()[1].isChecked():
                    item_widget.children()[1].setChecked(False)
                    self.sections_selected_count -= 1
                    ElementStyles.unselectedListItem(item_widget)
            item_widget.children()[1].stateChanged.connect(lambda state, item_widget=item_widget: self.multipleSectionsSelected(item_widget))

        if self.sections_selected_count > 0:
            self.addButtonsToSLSectionActionButtonsLayout()
        else:
            self.clearSLSectionActionButtonLayout()

    def clearSLSectionActionButtonLayout(self):
        try: self.remove_sections_from_sl_button.clicked.disconnect()
        except: pass
        for i in reversed(range(self.sl_section_action_button_layout.count())):
            self.sl_section_action_button_layout.itemAt(i).widget().setParent(None)

    def addButtonsToSLSectionActionButtonsLayout(self):
        self.clearSLSectionActionButtonLayout()
        if self.remove_sections_from_sl_button is None:
            self.remove_sections_from_sl_button = QPushButton("Remove Sections from Study List")
            self.remove_sections_from_sl_button.setStyleSheet("background-color: rgb(255, 76, 17); color: white")
            self.remove_sections_from_sl_button.setCursor(Qt.PointingHandCursor)
        self.sl_section_action_button_layout.addWidget(self.remove_sections_from_sl_button)
        self.disconnectWidget(self.remove_sections_from_sl_button)
        self.remove_sections_from_sl_button.clicked.connect(lambda state, selected_study_list=self.selected_study_list: self.removeSectionsFromStudyList(selected_study_list))

    def multipleSectionsSelected(self, item_widget):
        if item_widget.children()[1].isChecked():
            self.sections_selected_count += 1
            ElementStyles.highlightListItem(item_widget)
        else:
            self.sections_selected_count -= 1
            ElementStyles.unselectedListItem(item_widget)
        if self.sections_selected_count > 0:
            self.addButtonsToSLSectionActionButtonsLayout()
        else:
            self.clearSLSectionActionButtonLayout()


    def createNewSLCollection(self):
        while self.create_new_coll_button.isDown():
            continue
        if self.create_new_coll_lineedit.text() is not None and len(self.create_new_coll_lineedit.text()) != 0:
            coll_id = self.generateCode()
            new_list_tuple = (coll_id, self.create_new_coll_lineedit.text(), None)
            self.db_interface.insertEntry("Study List Collection", new_list_tuple)
            self.create_new_coll_lineedit.clear()
            self.updateSLCollectionsDict()

            listitem = self.sl_scroll_area_element.createWidget("Study List Collection", next(item for item in self.study_list_collections if item["CollectionID"] == coll_id))
            listitem.setFixedHeight(33)
            self.sl_scroll_area_element.scroll_area_layout.addWidget(listitem)
            self.sl_scroll_area_element.count += 1
            self.sl_scroll_area_element.scroll_area_layout.setSpacing(self.sl_scroll_area_element.vertical_spacing)
            self.sl_scroll_area_element.scroll_area_layout.addStretch()


    def addNewStudyList(self):
        while self.add_new_sl_button.isDown():
            continue
        if self.add_new_sl_lineedit.text() is not None and len(self.add_new_sl_lineedit.text()) != 0:
            if self.add_new_sl_lineedit.text() not in [study_list["StudyListName"] for study_list in self.study_lists]:
                new_tag = self.generateCode()
                new_list_tuple = (new_tag, self.add_new_sl_lineedit.text(), date.today().strftime("%m/%d/%Y"))
                self.db_interface.insertEntry("Study List", new_list_tuple)
                self.add_new_sl_lineedit.clear()
                
                all_tags = ""
                uncat_collection = [coll for coll in self.study_list_collections if coll["CollectionName"] == "Uncategorized"][0]
                if uncat_collection["Tags"] is None or uncat_collection["Tags"] == "":
                    all_tags = new_tag
                elif new_tag not in uncat_collection["Tags"].split(","):
                    all_tags = ",".join([uncat_collection["Tags"], new_tag])
                update_list = [all_tags, uncat_collection["CollectionID"]]
                self.db_interface.updateEntry("Update SL Collection Tags", update_list)
                # self.study_lists = self.db_interface.fetchEntries("Study Lists", [])
                # self.study_list_collections = self.db_interface.fetchEntries("Study List Collections", [])
                # self.sl_list_element.setList("Study List", self.study_lists)
                self.updateSLCollectionsDict()

                self.study_lists_listwidget.itemClicked.connect(lambda: self.studyListClicked(self.study_lists_listwidget.itemWidget(self.study_lists_listwidget.currentItem())))
                for i in range(self.study_lists_listwidget.count()):
                    item_widget = self.study_lists_listwidget.itemWidget(self.study_lists_listwidget.item(i))
                    #item_widget.children()[-1].clicked.connect(lambda state, item_widget=item_widget: self.deleteStudyList(item_widget))
                self.selected_study_list = None
                self.selected_section = None
                self.prev_study_list_item_widget = None
                self.prev_section_list_widget_item = None
                self.sections_selected_count = 0
                self.clearExercisesGrid()
                self.sl_sections_listwidget.clear()




    def deleteStudyList(self, item_widget):
        study_list_name = item_widget.children()[2].text()
        tag = [entry["StudyListID"] for entry in self.study_lists if entry["StudyListName"] == study_list_name][0]
        for section in self.sl_collections_dict[self.selected_collection][study_list_name]["Sections"]:
            for ex in section["Exercises"]:
                tags = ex["Tags"].split(",")
                tags.pop(tags.index(tag))
                ex["Tags"] = ",".join(tags)
                update_entry = [ex["Tags"], ex["TextbookID"], ex["ExerciseID"]]
                self.db_interface.updateEntry("Update Exercise Tag", update_entry)

        uncat_collection = [coll for coll in self.study_list_collections if coll["CollectionName"] == "Uncategorized"][0]
        tags = uncat_collection["Tags"].split(",")
        tags.pop(tags.index(tag))
        uncat_collection["Tags"] = ",".join(tags)
        update_entry = [",".join(tags), uncat_collection["CollectionID"]]
        self.db_interface.updateEntry("Update SL Collection Tags", update_entry)
        self.db_interface.deleteEntry("Study List", [tag])
        self.showPage()

        # self.updateSLCollectionsDict()
        #
        # for i in range(self.study_lists_listwidget.count()):
        #     item_widget = self.study_lists_listwidget.itemWidget(self.study_lists_listwidget.item(i))
        #     if len(item_widget.children()) > 4:
        #         item_widget.children()[-1].clicked.connect(lambda state, item_widget=item_widget: self.deleteStudyList(item_widget))
        # self.selected_study_list = None
        # self.selected_section = None
        # self.prev_study_list_item_widget = None
        # self.prev_section_list_widget_item = None
        # self.sections_selected_count = 0
        # self.clearExercisesGrid()
        # self.sl_sections_listwidget.clear()
        # self.progress_donut_label.clear()




    def removeSectionsFromStudyList(self, selected_study_list):
        for i in range(self.sl_sections_listwidget.count()):
            item_widget = self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i))
            if item_widget.children()[1].isChecked():
                section = [sect for sect in self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"] if sect["TextbookID"] == item_widget.children()[3].text() and sect["ChapterNumber"] == item_widget.children()[4].text() and sect["SectionNumber"] == item_widget.children()[5].text()][0]
                for ex in section["Exercises"]:
                    tags = ex["Tags"].split(",")
                    tags.pop(tags.index(selected_study_list))
                    ex["Tags"] = ",".join(tags)
                    update_entry = [ex["Tags"], ex["TextbookID"], ex["ExerciseID"]]
                    self.db_interface.updateEntry("Update Exercise Tag", update_entry)
        self.updateSLCollectionsDict()
        if self.prev_study_list_item_widget is not None:
            self.studyListClicked(self.prev_study_list_item_widget)
        self.clearSLSectionActionButtonLayout()

    def studyListSectionClicked(self, item_widget):
        self.sb_frame.setStyleSheet("background-color: gray")
        self.start_button_2.setStyleSheet("color: black")
        self.start_button_2.setEnabled(False)
        self.selected_section = [sect for sect in self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"] if sect["TextbookID"] == item_widget.children()[3].text() and sect["ChapterNumber"] == item_widget.children()[4].text() and sect["SectionNumber"] == item_widget.children()[5].text()][0]

        self.setExercisesButtons()
        textbook_info = self.db_interface.fetchEntries("Textbook Info", [self.selected_section["TextbookID"]])[0]
        self.category_info_label_2.setText(str(textbook_info["Category"]))
        self.textbook_info_label_2.setText(" - ".join([textbook_info["Authors"], textbook_info["Title"], textbook_info["Edition"]]))
        if self.prev_section_list_widget_item is not None:
            if self.prev_section_list_widget_item.children()[1].isChecked():
                ElementStyles.highlightListItem(self.prev_section_list_widget_item)
            else:
                ElementStyles.unselectedListItem(self.prev_section_list_widget_item)
        ElementStyles.selectedListItem(item_widget)
        self.prev_section_list_widget_item = item_widget

        self.setTextbookdir()
        self.open_txtbk_dir_button_2.clicked.connect(lambda: os.startfile(self.txtbk_dir))

    def setTextbookdir(self):
        txtbk_info = self.db_interface.fetchEntries("Textbook Info", [self.selected_section["TextbookID"]])[0]
        if txtbk_info["Edition"] != "1st":
            self.txtbk_dir = os.path.join(Config.MAIN_DIR, txtbk_info["Category"], " - ".join([txtbk_info["Authors"], txtbk_info["Title"], txtbk_info["Edition"]]), "Textbook")
        else:
            self.txtbk_dir = os.path.join(Config.MAIN_DIR, txtbk_info["Category"], " - ".join([txtbk_info["Authors"], txtbk_info["Title"]]), "Textbook")


    def updateGradeDistribution(self):
        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesA"] = 0
        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesB"] = 0
        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesC"] = 0
        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesD"] = 0
        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesF"] = 0
        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NoGrade"] = 0
        for section in self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"]:
            section["NumExercisesA"] = 0
            section["NumExercisesB"] = 0
            section["NumExercisesC"] = 0
            section["NumExercisesD"] = 0
            section["NumExercisesF"] = 0
            section["NoGrade"] = 0
            for ex in section["Exercises"]:
                if ex["Attempts"] > 0:
                    if datetime.strptime(ex["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
                        if ex["Grade"] == 'A':
                            section["NumExercisesA"] += 1
                            self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesA"] += 1
                        elif ex["Grade"] == 'B':
                            section["NumExercisesB"] += 1
                            self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesB"] += 1
                        elif ex["Grade"] == 'C':
                            section["NumExercisesC"] += 1
                            self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesC"] += 1
                        elif ex["Grade"] == 'D':
                            section["NumExercisesD"] += 1
                            self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesD"] += 1
                        elif ex["Grade"] == 'F':
                            section["NumExercisesF"] += 1
                            self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NumExercisesF"] += 1
                    else:
                        section["NoGrade"] += 1
                        self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NoGrade"] += 1
                elif ex["SolutionExists"] == 'True':
                    section["NoGrade"] += 1
                    self.sl_collections_dict[self.selected_collection][self.selected_study_list]["NoGrade"] += 1


    def updateSLSectionList(self):
        #self.updateGradeDistribution()
            # progress_label = self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[7]
            # self.sl_sections_listwidget.updateProgressBar(progress_label, sect_entry)
        self.sl_sections_listwidget.setList("Selected Study List Sections", self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"])

        if self.prev_section_list_widget_item is not None:
            for i in range(self.sl_sections_listwidget.count()):
                if self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[3].text() == self.prev_section_list_widget_item.children()[3].text():
                    if self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[4].text() == self.prev_section_list_widget_item.children()[4].text():
                        if self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[5].text() == self.prev_section_list_widget_item.children()[5].text():
                            self.prev_section_list_widget_item = self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i))
                            break
            self.studyListSectionClicked(self.prev_section_list_widget_item)

    def clearExercisesGrid(self):
        for i in reversed(range(self.sl_exercises_grid.count())):
            self.sl_exercises_grid.itemAt(i).widget().setParent(None)


    def setExercisesButtons(self):
        self.prev_selected_exercise_num = None
        self.clearExercisesGrid()
        self.chapter_info_label_2.setText(str(self.selected_section["ChapterNumber"]))
        self.section_info_label_2.setText(str(self.selected_section["SectionNumber"]))
        count = len(self.selected_section["Exercises"])
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
                    ex_num = int(self.selected_section["Exercises"][index]["ExerciseID"].split(".")[-1])
                    self.button = QPushButton(str(ex_num))
                    self.button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                    self.button.setCheckable(True)
                    ElementStyles.lightShadow(self.button)
                    if self.selected_section["Exercises"][index]["SolutionExists"] is not None:
                        if eval(self.selected_section["Exercises"][index]["SolutionExists"]):
                            if eval(self.selected_section["Exercises"][index]["Seen"]):
                                grade = self.selected_section["Exercises"][index]["Grade"]
                                if grade in Config.EXERCISE_GRADE_COLORS.keys() and datetime.strptime(self.selected_section["Exercises"][index]["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
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
                    self.sl_exercises_grid.addWidget(self.button, i, j)
        else:
            label = QLabel("\n\n\n\n\nNo Exercises!")
            color = "white"
            label.setStyleSheet("background-color : " + color)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFont(QFont("Arial", 12))
            label.resize(60, 80)
            self.sl_exercises_grid.addWidget(label, 0, 0)

    def showExerciseStats(self, num):
        self.sb_frame.setStyleSheet("background-color: rgb(0, 170, 127)")
        self.start_button_2.setStyleSheet("color: white")
        self.start_button_2.setEnabled(True)
        if self.prev_selected_exercise_num is not None:
            last_grid_index = [self.selected_section["Exercises"].index(entry) for entry in self.selected_section["Exercises"] if int(entry["ExerciseID"].split(".")[-1]) == self.prev_selected_exercise_num][0]
            self.sl_exercises_grid.itemAt(last_grid_index).widget().setEnabled(True)
            self.sl_exercises_grid.itemAt(last_grid_index).widget().toggle()
            self.sl_exercises_grid.itemAt(last_grid_index).widget().setStyleSheet("background-color : " + self.prev_selected_exercise_bgcolor)
        grid_index, exercise_stats = [[self.selected_section["Exercises"].index(entry), entry] for entry in self.selected_section["Exercises"] if int(entry["ExerciseID"].split(".")[-1]) == num][0]
        self.prev_selected_exercise_num = num
        self.sl_exercises_grid.itemAt(grid_index).widget().setEnabled(False)
        self.sl_exercises_grid.itemAt(grid_index).widget().setStyleSheet("background-color : lightblue")
        if eval(exercise_stats["Seen"]) and exercise_stats["Attempts"] > 0:
            self.ex_stats_info_grade_label_2.setText(str(exercise_stats["Grade"]))
            self.ex_stats_info_lastattempt_label_2.setText(str(exercise_stats["LastAttempted"]) + " -- " + str(exercise_stats["LastAttemptTime"]))
            self.ex_stats_info_totalattempts_label_2.setText(str(exercise_stats["Attempts"]))
            self.ex_stats_info_averagetime_label_2.setText(str(exercise_stats["AverageTime"]))
            if datetime.strptime(exercise_stats["LastAttempted"], '%m/%d/%Y').date() >= datetime.strptime(self.date_filter, '%m/%d/%Y').date():
                self.prev_selected_exercise_bgcolor = "rgb" + str(Config.EXERCISE_GRADE_COLORS[exercise_stats["Grade"]])
            else:
                self.prev_selected_exercise_bgcolor = "gray"
        elif eval(exercise_stats["Seen"]) and exercise_stats["Attempts"] == 0:
            self.ex_stats_info_grade_label_2.setText("N/A")
            self.ex_stats_info_lastattempt_label_2.setText("N/A")
            self.ex_stats_info_totalattempts_label_2.setText("N/A")
            self.ex_stats_info_averagetime_label_2.setText("N/A")
            self.prev_selected_exercise_bgcolor = "gray"
        else:
            self.ex_stats_info_grade_label_2.setText("N/A")
            self.ex_stats_info_lastattempt_label_2.setText("N/A")
            self.ex_stats_info_totalattempts_label_2.setText("N/A")
            self.ex_stats_info_averagetime_label_2.setText("N/A")
            self.prev_selected_exercise_bgcolor = "white"
        # for i in reversed(range(self.ex_study_list_tablewidget.rowCount())):
        #     self.ex_study_list_tablewidget.removeRow(i)
        self.disconnectWidget(self.start_button_2)
        self.start_button_2.clicked.connect(lambda state, num=num, exercises=self.selected_section["Exercises"]: self.practice_page.showPage(num, exercises))


    def sortSectionsListBy(self, column):
        selected_sl_sections = self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"]
        if column == "TextbookID":
            self.CN_sort_order = 1
            self.SN_sort_order = 1
            self.progress_sort_order = None
            self.count_sort_order = None
            if self.TID_sort_order is None or self.TID_sort_order == -1:
                self.TID_sort_order = 1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: x['TextbookID'], reverse=True)
            elif self.TID_sort_order == 1:
                self.TID_sort_order = -1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: x['TextbookID'])
        elif column == "ChapterNumber":
            self.TID_sort_order = None
            self.SN_sort_order = 1
            self.count_sort_order = None
            self.progress_sort_order = None
            if self.CN_sort_order is None or self.CN_sort_order == -1:
                self.CN_sort_order = 1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: (int(x["ChapterNumber"]) if x["ChapterNumber"].isdigit() else 999, int(x["SectionNumber"]) if x["SectionNumber"].isdigit() else 999), reverse=True)
            elif self.CN_sort_order == 1:
                self.CN_sort_order = -1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: (int(x["ChapterNumber"]) if x["ChapterNumber"].isdigit() else 999, int(x["SectionNumber"]) if x["SectionNumber"].isdigit() else 999))
        elif column == "SectionNumber":
            self.TID_sort_order = None
            self.CN_sort_order = 1
            self.count_sort_order = None
            self.progress_sort_order = None
            if self.SN_sort_order is None or self.SN_sort_order == -1:
                self.SN_sort_order = 1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: (int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999, int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999), reverse=True)
            elif self.SN_sort_order == 1:
                self.SN_sort_order = -1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: (int(x['SectionNumber']) if x['SectionNumber'].isdigit() else 999, int(x['ChapterNumber']) if x['ChapterNumber'].isdigit() else 999))
        elif column == "Count":
            self.TID_sort_order = None
            self.CN_sort_order = 1
            self.SN_sort_order = 1
            self.progress_sort_order = None
            if self.count_sort_order is None or self.count_sort_order == -1:
                self.count_sort_order = 1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: x['Count'], reverse=True)
            elif self.count_sort_order == 1:
                self.count_sort_order = -1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: x['Count'])
        elif column == "Progress":
            self.TID_sort_order = None
            self.CN_sort_order = 1
            self.SN_sort_order = 1
            self.count_sort_order = None
            for sect_entry in selected_sl_sections:
                if sect_entry["Count"] > 0:
                    weighted_count_A = sect_entry["NumExercisesA"] * 5
                    weighted_count_B = sect_entry["NumExercisesB"] * 4
                    weighted_count_C = sect_entry["NumExercisesC"] * 3
                    weighted_count_D = sect_entry["NumExercisesD"] * 2
                    weighted_count_F = sect_entry["NumExercisesF"] * 1
                    sect_entry["Progress"] = (weighted_count_A + weighted_count_B + weighted_count_C + weighted_count_D + weighted_count_F) / (sect_entry["Count"] * 5)
                else:
                    sect_entry["Progress"] = 0.0
            if self.progress_sort_order is None or self.progress_sort_order == 1:
                self.progress_sort_order = -1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: x['Progress'])
            elif self.progress_sort_order == -1:
                self.progress_sort_order = 1
                selected_sl_sections = sorted(selected_sl_sections, key=lambda x: x['Progress'], reverse=True)



        self.sl_sections_listwidget.setList("Selected Study List Sections", selected_sl_sections)
        self.disconnectWidget(self.sl_sections_listwidget)
        self.sl_sections_listwidget.itemClicked.connect(lambda: self.studyListSectionClicked(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.currentItem())))
        self.prev_section_list_widget_item = None
        if len(self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"]) > 0:
            for i in range(self.sl_sections_listwidget.count()):
                exercises = self.sl_collections_dict[self.selected_collection][self.selected_study_list]["Sections"][i]["Exercises"]
                if len(exercises) > 0:
                    num = int(exercises[0]["ExerciseID"].split(".")[-1])
                    self.disconnectWidget(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[-2])
                    self.disconnectWidget(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[1])
                    self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[-2].clicked.connect(lambda state, num=num, exercises=exercises: self.practice_page.showPage(num, exercises))
                    self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i)).children()[1].stateChanged.connect(lambda state, i=i: self.multipleSectionsSelected(self.sl_sections_listwidget.itemWidget(self.sl_sections_listwidget.item(i))))
            self.clearSLSectionActionButtonLayout()



    def generateCode(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))



