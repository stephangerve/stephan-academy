from ContentPages.ClassPage import Page


class DashboardPage(Page):
    ui = None



    def __init__(self, ui):
        Page.__init__(self, "Dashboard", 0)
        self.ui = ui
        self.initUI()


    def initUI(self):
        pass

    def referenceObjects(self):
        pass