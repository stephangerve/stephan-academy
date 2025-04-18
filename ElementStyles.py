# Designs that are used by multiple objects
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5 import QtCore

def removeShadow(object):
    object.setGraphicsEffect(None)

def regularShadow(object):
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(0, 2)
    shadow.setColor(QColor(38, 78, 119, 127))
    shadow.setBlurRadius(10)
    object.setGraphicsEffect(shadow)

def lightShadow(object):
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(0, 1)
    shadow.setColor(QColor(38, 78, 119, 127))
    shadow.setBlurRadius(5)
    object.setGraphicsEffect(shadow)

def lightShadow2(object):
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(0, 1)
    shadow.setColor(QColor(150, 150, 150, 127))
    shadow.setBlurRadius(5)
    object.setGraphicsEffect(shadow)


def selectedListItem(listitemwidget):
    listitemwidget.setStyleSheet("background-color: lightgray")

def unselectedListItem(listitemwidget):
    hoverEffect(listitemwidget)

def hoverEffect(qobject):
    qobject.setStyleSheet("QObject::hover{background-color : rgb(238, 238, 236);};")

def hoverEffectSideBar(qobject):
    qobject.setStyleSheet("QObject::hover{background-color : #556785;};")

def highlightListItem(item_widget):
    item_widget.setStyleSheet("background-color: #ccf6ff")

########################################################################################################################
# def redBackground(object):
#     object.setStyleSheet(object.styleSheet() + ";background-color: #FB4D3D;")
#
# def whiteBackground(object):
#     object.setStyleSheet(object.styleSheet() + ";background-color: #ffffff;")
#
# def greenBackground(object):
#     object.setStyleSheet(object.styleSheet() + ";background-color: #6DA34D;")
#
# def navyBlueBackground(object):
#     object.setStyleSheet(object.styleSheet() + ";background-color: #2A4D87;")
#
# def orangeBackround(object):
#     object.setStyleSheet(object.styleSheet() + "background-color: #CC7027;")
#
# def roundButton(object):
#     object.setStyleSheet("border-radius: 20px;"
#                          "color: rgb(238, 238, 236);"
#                          "font: 12pt \"Ubuntu\";")
#
#
# def selectedPageButton(pushbutton):
#     pushbutton.setStyleSheet("border-width: 3px; border-style: solid; "
#                              "border-color: rgb(238, 238, 236) rgb(238, 238, 236) rgb(238, 238, 236) #CC7027; "
#                              "background-color: rgb(238, 238, 236);"
#                              "text-align:left;"
#                              "padding-left:37px;"
#                              "color: #4e5256")
#
#
# def unselectedPageButton(pushbutton):
#     pushbutton.setStyleSheet("border: none; "
#                               "background-color: rgb(58, 74, 97); "
#                               "color: #eeeeec; "
#                               "text-align:left; "
#                               "padding-left:40px")
#
#
# def unselectedBottomPageButton(pushbutton):
#     pushbutton.setStyleSheet("border: none; "
#                              "background-color: #232d3a;"
#                              "color: #eeeeec; "
#                              "text-align:left; "
#                              "padding-left:40px")
#
# def whiteRoundSquare(object):
#     object.setStyleSheet("border-radius: 5px; background-color: white")

