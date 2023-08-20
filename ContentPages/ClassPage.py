from abc import abstractmethod
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QCheckBox

class Page(QWidget):
    __page_name = None
    __page_number = None


    def __init__(self, page_number):
        super().__init__()
        #self.__page_name = page_name
        self.__page_number = page_number

    # @abstractmethod
    # def activate(self):
    #     raise NotImplementedError("Method must be implemented: \"activate\"")
    #
    # @abstractmethod
    # def deactivate(self):
    #     raise NotImplementedError("Method must be implemented: \"deactivate\"")
    @abstractmethod
    def referenceObjects(self):
        raise NotImplementedError("Method must be implemented: \"deactivate\"")

    @abstractmethod
    def showPage(self):
        raise NotImplementedError("Method must be implemented: \"deactivate\"")

    def exitPage(self):
        pass

    # @property
    # def page_name(self):
    #     return self.__page_name

    # @page_name.setter
    # def page_name(self, page_name):
    #     self.__page_name = page_name

    @property
    def page_number(self):
        return self.__page_number

    @page_number.setter
    def page_number(self, page_number):
        self.__page_number = page_number

    def disconnectWidget(self, widget):
        if type(widget) == QPushButton:
            try:
                widget.clicked.disconnect()
            except:
                pass
        elif type(widget) == QListWidget:
            try:
                widget.itemClicked.disconnect()
            except:
                pass
        elif type(widget) == QCheckBox:
            try:
                widget.stateChanged.disconnect()
            except:
                pass

