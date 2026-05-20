from cardapp.test.sels.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

class PayPage(BasePage):
    URL = 'http://127.0.0.1:5000/pay'

    MOMO_BUTTON = (By.ID, 'pay-momo')
    DISCOUNT_CODE = (By.ID, 'discount-code')
    APPLY_BUTTON = (By.CSS_SELECTOR, 'body > section > div > div > div:nth-child(2) > div > div.card-body > div.input-group.mb-2 > button')
    PAY_BUTTON = (By.CSS_SELECTOR, '#btn-pay')


    def open_page(self, url=URL):
        self.open(url)

    def apply_discount_code(self, discount_code):
        self.click(*self.MOMO_BUTTON)
        self.driver.implicitly_wait(1)
        self.typing(*self.DISCOUNT_CODE, discount_code)
        self.driver.implicitly_wait(1)
        self.click(*self.APPLY_BUTTON)
        self.driver.implicitly_wait(1)

    def apply_pay(self):
        self.driver.implicitly_wait(1)
        self.click(*self.PAY_BUTTON)