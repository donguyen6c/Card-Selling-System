from cardapp.test.sels.pages.LoginPage import LoginPage
from cardapp.test.test_base import driver
from selenium.webdriver.common.by import By

import time



def test_login_success(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')

    time.sleep(2)
    assert driver.current_url == 'http://127.0.0.1:5000/'
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\login_success.png")
    e = driver.find_element(By.CSS_SELECTOR, '#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > a > span')
    assert 'user' in e.text

def test_login_redirect(driver):
    login = LoginPage(driver=driver)
    login.open_page('http://127.0.0.1:5000/login?next=/carts')
    login.login('user', '123456')

    time.sleep(2)
    assert driver.current_url == 'http://127.0.0.1:5000/carts'
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\login_redirect.png")




def test_login_wrong_info(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('taikhoaisai', 'matkhausai')

    time.sleep(1)
    e = driver.find_element(By.CSS_SELECTOR, "body > section > form > div.alert.alert-danger")
    assert 'Tên đăng nhập hoặc mật khẩu không chính xác!' in e.text
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\login_wrong_info.png")


def test_logout(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')

    time.sleep(2)
    e = driver.find_element(By.CSS_SELECTOR,
                            "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > a")
    e.click()
    time.sleep(1)

    info = driver.find_element(By.CSS_SELECTOR,
                               "#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.dropdown > ul > li:nth-child(3) > a")
    info.click()
    time.sleep(2)
    assert driver.current_url == 'http://127.0.0.1:5000/login'
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\logout.png")

def test_login_admin(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('admin', '123456')

    time.sleep(2)
    assert driver.current_url == 'http://127.0.0.1:5000/admin/'
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\login_admin.png")


