from selenium.webdriver.common.by import By

from cardapp.test.sels.pages.BasePage import BasePage

class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'
    USERNAME = (By.ID, 'username')
    PASSWORD = (By.ID, 'pwd')
    LOGIN_BUTTON = (By.CSS_SELECTOR, 'body > section > form > div:nth-child(3) > button')

    def open_page(self, url=URL):
        self.open(url)

    def login(self, username, password):
        self.typing(*self.USERNAME, username)
        self.driver.implicitly_wait(1)
        self.typing(*self.PASSWORD, password)
        self.driver.implicitly_wait(1)
        self.click(*self.LOGIN_BUTTON)