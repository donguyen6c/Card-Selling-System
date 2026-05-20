from cardapp.test.sels.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'
    PHONE_CARD_BUTTON = (By.CSS_SELECTOR, '#tab-main-phone')
    VIETTEL_BUTTON = (By.CSS_SELECTOR, '#tab-phone-1')
    FIFTY_VIETTEL_BUTTON = (By.CSS_SELECTOR, '#content-phone-1 > div > div:nth-child(3) > button')

    GAME_CARD_BUTTON = (By.CSS_SELECTOR, '#tab-main-game')
    GARENA_BUTTON = (By.CSS_SELECTOR, '#tab-game-4')
    FIFTY_GARENA_BUTTON = (By.CSS_SELECTOR, '#content-game-4 > div > div:nth-child(2) > button')

    APPLY_BUTTON = (By.CSS_SELECTOR, '#btn-buy')

    def open_page(self):
        self.open(self.URL)

    def add_to_cart_phone(self):
        self.click(*self.PHONE_CARD_BUTTON)
        self.driver.implicitly_wait(1)
        self.click(*self.VIETTEL_BUTTON)
        self.driver.implicitly_wait(1)
        self.click(*self.FIFTY_VIETTEL_BUTTON)
        self.driver.implicitly_wait(1)
        self.click(*self.APPLY_BUTTON)

        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()


    def add_to_card_game(self):
        self.click(*self.GAME_CARD_BUTTON)
        self.driver.implicitly_wait(1)
        self.click(*self.GARENA_BUTTON)
        self.driver.implicitly_wait(1)
        self.click(*self.FIFTY_GARENA_BUTTON)
        self.driver.implicitly_wait(1)
        self.click(*self.APPLY_BUTTON)

        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()

