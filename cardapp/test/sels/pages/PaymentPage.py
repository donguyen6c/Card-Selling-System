from cardapp.test.sels.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PaymentPage(BasePage):
    URL = "http://127.0.0.1:5000/payment"
    CONFIRM_BTN = (By.CSS_SELECTOR, "#btn-confirm-pay")
    def open_page(self, url=URL):
        self.open(url)

    def confirm_payment(self):
        self.click(*self.CONFIRM_BTN)

        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()