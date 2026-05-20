from selenium.webdriver import Keys
import os

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def find(self, by, value):
        return self.driver.find_element(by, value)

    def finds(self, by, value):
        return self.driver.find_elements(by, value)

    def typing(self, by, value, text):
        e = self.find(by, value)

        e.send_keys(Keys.CONTROL + "a")
        e.send_keys(Keys.DELETE)

        e.send_keys(text)

    def click(self, by, value):
        e = self.find(by, value)
        e.click()

    def open(self, url):
        self.driver.get(url)

    def upload_file(self, by, value, path):
        absolute_path = os.path.abspath(path)

        e = self.find(by, value)

        e.send_keys(absolute_path)