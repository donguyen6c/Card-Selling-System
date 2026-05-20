from cardapp.test.sels.pages.LoginPage import LoginPage

from cardapp.test.test_base import driver
from selenium.webdriver.common.by import By

from cardapp.test.sels.pages.ProfilePage import ProfilePage
import time



def test_update_name(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')

    time.sleep(2)
    e = driver.find_element(By.CSS_SELECTOR, "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > a")
    e.click()
    time.sleep(1)

    info = driver.find_element(By.CSS_SELECTOR, "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > ul > li:nth-child(1) > a")
    info.click()
    time.sleep(2)

    profile = ProfilePage(driver=driver)
    profile.open_page()
    profile.update_name("Test Username")
    time.sleep(1)
    profile.apply_update()
    time.sleep(2)

    e = driver.find_element(By.ID, 'name')
    assert e.get_attribute("value") == "Test Username"
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\update_name.png")

def test_update_not_exist_email(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')

    time.sleep(2)
    e = driver.find_element(By.CSS_SELECTOR,
                            "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > a")
    e.click()
    time.sleep(1)

    info = driver.find_element(By.CSS_SELECTOR,
                               "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > ul > li:nth-child(1) > a")
    info.click()
    time.sleep(2)

    profile = ProfilePage(driver=driver)
    profile.open_page()
    profile.update_email("testemail@gmail.com")
    time.sleep(1)
    profile.apply_update()
    time.sleep(2)

    e = driver.find_element(By.ID, 'email')
    assert e.get_attribute("value") == "testemail@gmail.com"
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\update_email.png")


def test_update_existed_email(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')

    time.sleep(2)
    e = driver.find_element(By.CSS_SELECTOR,
                            "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > a")
    e.click()
    time.sleep(1)

    info = driver.find_element(By.CSS_SELECTOR,
                               "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > ul > li:nth-child(1) > a")
    info.click()
    time.sleep(2)

    profile = ProfilePage(driver=driver)
    profile.open_page()
    profile.update_email("existemail@gmail.com")
    time.sleep(1)
    profile.apply_update()
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, '#profileForm > div.alert.alert-danger.alert-dismissible.fade.show.shadow-sm')
    assert 'Email này đã được sử dụng bởi một tài khoản khác' in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\update_existed_email.png")

