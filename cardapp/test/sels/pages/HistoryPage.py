from cardapp.test.sels.pages.BasePage import BasePage


class HistoryPage(BasePage):
    URL = 'http://127.0.0.1:5000/users/current-user/transactions'

    def open_page(self):
        self.open(self.URL)

