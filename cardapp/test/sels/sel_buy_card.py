from cardapp.test.sels.pages.CartPage import CartPage
from cardapp.test.sels.pages.HistoryPage import HistoryPage
from cardapp.test.sels.pages.LoginPage import LoginPage
from cardapp.test.sels.pages.PayPage import PayPage
from cardapp.test.sels.pages.PaymentPage import PaymentPage
from cardapp.test.test_base import driver
from selenium.webdriver.common.by import By

from cardapp.test.sels.pages.HomePage import HomePage
import time


def test_add_to_cart(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 700)')
    time.sleep(2)
    home.add_to_cart_phone()
    time.sleep(2)
    home.add_to_card_game()

    cart = CartPage(driver=driver)
    cart.open_page()
    driver.implicitly_wait(2)
    e = driver.find_element(By.CSS_SELECTOR, '#collapsibleNavbar > ul.navbar-nav.ms-auto.align-items-center > li.nav-item.me-4.mb-2.mb-lg-0 > a > span')
    assert int(e.text) == 2
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\add_to_cart.png")


def test_pay_with_limited_discount(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 700)')
    time.sleep(2)
    home.add_to_cart_phone()
    time.sleep(2)
    home.add_to_card_game()

    cart = CartPage(driver=driver)
    cart.open_page()
    cart.add_to_card_game()
    time.sleep(2)
    cart.add_to_card_phone()
    time.sleep(2)
    cart.click_checkout()
    time.sleep(2)

    pay = PayPage(driver=driver)
    pay.open_page()
    pay.apply_discount_code('GGS1')
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, '#discount-msg > span')
    assert 'đã hết lượt sử dụng' in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\pay_with_limited_discount.png")


def test_pay_with_wrong_discount_code(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 700)')
    time.sleep(2)
    home.add_to_cart_phone()
    time.sleep(2)
    home.add_to_card_game()

    cart = CartPage(driver=driver)
    cart.open_page()
    cart.add_to_card_game()
    time.sleep(1)
    cart.add_to_card_phone()
    time.sleep(1)
    cart.click_checkout()
    time.sleep(1)

    pay = PayPage(driver=driver)
    pay.open_page()
    pay.apply_discount_code('NOT_EXIST')

    e = driver.find_element(By.CSS_SELECTOR, '#discount-msg > span')
    assert 'Mã giảm giá không tồn tại!' in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\pay_with_wrong_discount_code.png")


def test_pay_with_expired_discount(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 700)')
    time.sleep(2)
    home.add_to_cart_phone()
    time.sleep(2)
    home.add_to_card_game()

    cart = CartPage(driver=driver)
    cart.open_page()
    cart.add_to_card_game()
    time.sleep(1)
    cart.add_to_card_phone()
    time.sleep(1)
    cart.click_checkout()
    time.sleep(1)

    pay = PayPage(driver=driver)
    pay.open_page()
    pay.apply_discount_code('GARENA50')

    e = driver.find_element(By.CSS_SELECTOR, '#discount-msg > span')
    assert 'Mã giảm giá đã hết hạn!' in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\pay_with_expired_discount.png")

def test_pay_with_success_discount(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 700)')
    time.sleep(2)
    home.add_to_cart_phone()
    time.sleep(2)
    home.add_to_card_game()

    cart = CartPage(driver=driver)
    cart.open_page()
    time.sleep(1)
    cart.click_checkout()

    pay = PayPage(driver=driver)
    pay.open_page()
    pay.apply_discount_code('GAME50')
    time.sleep(2)
    pay.apply_pay()
    time.sleep(2)

    payment = PaymentPage(driver=driver)
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 600)')
    time.sleep(1)
    payment.confirm_payment()
    time.sleep(1)

    histories = HistoryPage(driver=driver)
    histories.open_page()
    e = driver.find_element(By.CSS_SELECTOR, '#historyAccordion .accordion-item:first-child .text-danger.fw-bold')
    assert '75,000' in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\pay_with_success_discount.png")

def test_pay_success_without_discount(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user', '123456')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 700)')
    time.sleep(2)
    home.add_to_cart_phone()
    time.sleep(2)
    home.add_to_card_game()

    cart = CartPage(driver=driver)
    cart.open_page()
    time.sleep(1)
    cart.click_checkout()

    pay = PayPage(driver=driver)
    pay.open_page()
    pay.apply_pay()
    time.sleep(2)

    payment = PaymentPage(driver=driver)
    driver.implicitly_wait(2)
    driver.execute_script('window.scrollTo(0, 600)')
    time.sleep(1)
    payment.confirm_payment()
    time.sleep(1)

    histories = HistoryPage(driver=driver)
    histories.open_page()
    e = driver.find_element(By.CSS_SELECTOR, '#historyAccordion .accordion-item:first-child .text-danger.fw-bold')
    assert '100,000' in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\pay_with_success_without_discount.png")