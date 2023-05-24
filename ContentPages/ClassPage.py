from abc import abstractmethod


class Page:
    __page_name = None
    __page_number = None


    def __init__(self, page_name, page_number):
        self.__page_name = page_name
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

    @property
    def page_name(self):
        return self.__page_name

    @page_name.setter
    def page_name(self, page_name):
        self.__page_name = page_name

    @property
    def page_number(self):
        return self.__page_number

    @page_number.setter
    def page_number(self, page_number):
        self.__page_number = page_number

