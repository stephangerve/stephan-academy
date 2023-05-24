import ElementStyles
from PyQt5.QtWidgets import QScrollBar, QHBoxLayout, QLabel, QWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5 import QtCore


class CounterElement():
    background_frame = None
    title_label = None
    value_label = None
    units_label = None

    def __init__(self, background_frame, title_label, value_label, units_label):
        self.background_frame = background_frame
        self.title_label = title_label
        self.value_label = value_label
        self.units_label = units_label
        ElementStyles.whiteRoundSquare(self.background_frame)
        ElementStyles.lightShadow(self.background_frame)


    def setValue(self, value):
        self.value_label.setText(str(value))

    def setTitle(self, title):
        self.title_label.setText(str(title))

    def setUnits(self, units):
        self.units_label.setText(str(units))



class IndicatorElement():
    background_frame = None
    title_label = None
    value_label = None

    def __init__(self, background_frame, title_label, value_label):
        self.background_frame = background_frame
        self.title_label = title_label
        self.value_label = value_label
        ElementStyles.whiteRoundSquare(self.background_frame)
        ElementStyles.lightShadow(self.background_frame)


    def setValue(self, value):
        self.value_label.setText(str(value))

    def setTitle(self, title):
        self.title_label.setText(str(title))




class ListElement():
    list_listwidget = None
    scroll_bar = None

    def __init__(self, list_listwidget):
        self.list_listwidget = list_listwidget

    def clear(self):
        self.list_listwidget.clear()


    def getItemIndex(self):
        return int(self.list_listwidget.currentItem().text())


    def setList(self, query_table_name, query_entries):
        self.list_listwidget.clear()
        row_number = 0
        for entry in query_entries:
            self.insert(self.listItemElement(query_table_name, entry))
        self.list_listwidget.setSpacing(3)
        self.scroll_bar = QScrollBar()
        self.scroll_bar.setStyleSheet("background : white;")
        self.list_listwidget.setVerticalScrollBar(self.scroll_bar)


    def insert(self, listItemElement):
        item = QListWidgetItem(self.list_listwidget)
        item.setBackground(QColor('#eeeeec'))
        item.setSizeHint(listItemElement.sizeHint())
        item.setText(str(self.list_listwidget.count()))
        self.list_listwidget.setItemWidget(item, listItemElement)


    def listItemElement(self, query_table_name, entry):
        elementLayout = QHBoxLayout()

        if query_table_name == "Categories":
            IDLabel = QLabel()
            IDLabel.setText(entry["ID"])
            IDLabel.setFixedWidth(200)
            IDLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(IDLabel)

        elif query_table_name == "Textbooks":
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
            #edLabel.setFixedWidth(180)
            edLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(edLabel)

        elif query_table_name == "Sections":
            IDLabel = QLabel()
            IDLabel.setText(entry["ID"])
            IDLabel.setFixedWidth(50)
            IDLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(IDLabel)

            sectLabel = QLabel()
            sectLabel.setText(entry["SectionNumber"])
            #sectLabel.setFixedWidth(50)
            sectLabel.setStyleSheet("color: #4e5256")
            elementLayout.addWidget(sectLabel)

        rowLabel = QLabel()
        elementLayout.addStretch()
        elementLayout.addWidget(rowLabel)

        elementLayout.setContentsMargins(5, 5, 5, 5)
        elementLayout.setSpacing(0)

        widget = QWidget()
        widget.setLayout(elementLayout)
        widget.setStyleSheet("background-color: #ffffff")

        return widget


class ButtonElement():
    pushbutton = None
    def __init__(self, pushbutton):
        self.pushbutton = pushbutton
        pushbutton.__init__()
        ElementStyles.roundButton(self.pushbutton)
        ElementStyles.whiteBackground(self.pushbutton)
        ElementStyles.lightShadow(self.pushbutton)

    def setText(self, string):
        self.pushbutton.setText(string)

    def disconnect(self):
        self.pushbutton.clicked.disconnect()



class PageButtonElement():
    pushbutton = None
    def __init__(self, pushbutton):
        self.pushbutton = pushbutton
        ElementStyles.unselectedPageButton(self.pushbutton)

    def setText(self, string):
        self.pushbutton.setText(string)

    def setIcon(self, path):
        self.pushbutton.setIcon(QIcon(QPixmap(path)))
        self.pushbutton.setIconSize(QtCore.QSize(20, 20))









