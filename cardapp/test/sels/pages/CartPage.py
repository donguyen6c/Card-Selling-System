from cardapp.test.sels.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

class CartPage(BasePage):
    URL = 'http://127.0.0.1:5000/carts'

    ADD_ITEM01_BUTTON = (By.ID, 'btn-plus-14')
    ADD_ITEM02_BUTTON = (By.ID, 'btn-plus-3')
    PAY_BUTTON = (By.CSS_SELECTOR, 'body > section > div.text-end.mt-3.mb-5 > a')
    def open_page(self):
        self.open(self.URL)


    def add_to_card_game(self):
        self.click(*self.ADD_ITEM01_BUTTON)
        self.driver.implicitly_wait(1)

    def add_to_card_phone(self):
        self.click(*self.ADD_ITEM02_BUTTON)
        self.driver.implicitly_wait(1)

    def click_checkout(self):
        self.click(*self.PAY_BUTTON)