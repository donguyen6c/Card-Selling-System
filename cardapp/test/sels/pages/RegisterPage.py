from selenium.webdriver.common.by import By

from cardapp.test.sels.pages.BasePage import BasePage

class RegisterPage(BasePage):
    URL = 'http://127.0.0.1:5000/register'
    NAME_INPUT = (By.ID, 'name')
    EMAIL_INPUT = (By.ID, 'email')
    USERNAME_INPUT = (By.ID, 'username')
    PASSWORD_INPUT = (By.ID, 'pwd')
    CONFIRM_INPUT = (By.ID, 'confirm')
    AVATAR_INPUT = (By.ID, 'avatar')
    REGISTER_BUTTON = (By.CSS_SELECTOR, 'body > section > form > div:nth-child(7) > button')

    def open_page(self, url=URL):
        self.open(url)

    def register(self, name, username, email, password, confirm, path_avatar):
        self.typing(*self.NAME_INPUT, name)
        self.driver.implicitly_wait(1)
        self.typing(*self.EMAIL_INPUT, email)
        self.driver.implicitly_wait(1)
        self.typing(*self.USERNAME_INPUT, username)
        self.driver.implicitly_wait(1)
        self.typing(*self.PASSWORD_INPUT, password)
        self.driver.implicitly_wait(1)
        self.typing(*self.CONFIRM_INPUT, confirm)
        self.driver.implicitly_wait(1)
        self.upload_file(*self.AVATAR_INPUT, path_avatar)
        self.driver.implicitly_wait(1)

    def apply_register(self):
        self.click(*self.REGISTER_BUTTON)