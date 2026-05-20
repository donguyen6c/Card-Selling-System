from cardapp.test.sels.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class ProfilePage(BasePage):
    URL = 'http://127.0.0.1:5000/users/current-user'
    NAME_INPUT = (By.ID, 'name')
    EMAIL_INPUT = (By.ID, 'email')
    SAVE_BUTTON = (By.CSS_SELECTOR, '#profileForm > div.row > div.col-md-8.ps-md-4 > div.d-grid > button')
    def open_page(self):
        self.open(self.URL)

    def update_name(self, name):
        self.typing(*self.NAME_INPUT, name)

    def update_email(self, email):
        self.typing(*self.EMAIL_INPUT, email)

    def apply_update(self):
        self.click(*self.SAVE_BUTTON)
        self.driver.implicitly_wait(1)


