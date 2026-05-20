from selenium.webdriver.common.alert import Alert
from cardapp.test.sels.pages.AdminPage import AdminPage
from cardapp.test.sels.pages.LoginPage import LoginPage
from cardapp.test.test_base import driver
from selenium.webdriver.common.by import By
import time


def test_delete_success(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("admin", "123456")
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, "#admin-navbar-collapse > ul.nav.navbar-nav.mr-auto > li:nth-child(5) > a")
    e.click()
    time.sleep(2)

    e = driver.find_element(
        By.CSS_SELECTOR,
        "table tbody tr:last-child .list-buttons-column form button span"
    )
    e.click()
    time.sleep(2)
    alert = Alert(driver)
    alert.accept()
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\delete_success.png")