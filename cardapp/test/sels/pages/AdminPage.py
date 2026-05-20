from cardapp.test.sels.pages.BasePage import BasePage


class AdminPage(BasePage):
    URL = 'http://127.0.0.1:5000/admin/'

    def open_page(self):
        self.open(self.URL)


