from cardapp.test.sels.pages.RegisterPage import RegisterPage
from cardapp.test.test_base import driver
from selenium.webdriver.common.by import By

import time



def test_register_success(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test01@gmail.com",
                      username="testacc01", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()
    time.sleep(5)
    assert driver.current_url == 'http://127.0.0.1:5000/login'
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_success.png")

def test_register_exist_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test123@gmail.com",
                      username="testacc01", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Username này đã được sử dụng!" in e.text
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_exist_username.png")

def test_register_exist_email(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test123@gmail.com",
                      username="testaccount2", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Email này đã được đăng ký!" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_exist_email.png")




def test_register_used_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test123@gmail.com",
                      username="testacc01", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Username này đã được sử dụng!" in e.text
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_used_username.png")

def test_register_invalid_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test123@gmail.com",
                      username="abcd", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Username phải ít nhất có 5 kí tự" in e.text
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_invalid_username.png")

def test_register_invalid_password(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test03@gmail.com",
                      username="abcde", password="12345aA",
                      confirm="12345aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Mật khẩu phải có ít nhất 8 kí tự" in e.text
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_invalid_password.png")


def test_register_used_email(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test123@gmail.com",
                      username="abcde", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Email này đã được đăng ký!" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_used_email.png")

def test_register_invalid_email(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test123@.com",
                      username="abcde", password="123456aA",
                      confirm="123456aA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Email không đúng định dạng!" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_invalid_email.png")

def test_register_password_without_number(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test05@gmail.com",
                      username="abcde", password="aaaaAAAA",
                      confirm="aaaaAAAA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Mật khẩu phải chứa ít nhất một chữ số" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_password_without_number.png")


def test_register_password_without_lower(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test05@gmail.com",
                      username="abcde", password="111111AA",
                      confirm="111111AA", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Mật khẩu phải chứa ít nhất một chữ thường" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_password_without_lower.png")

def test_register_password_without_upper(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test05@gmail.com",
                      username="abcde", password="111111aa",
                      confirm="111111aa ", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Mật khẩu phải chứa ít nhất một chữ hoa" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_password_without_upper.png")

def test_register_not_match_password(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register(name="abcd", email="test05@gmail.com",
                      username="abcde", password="111111aA",
                      confirm="111111aB ", path_avatar="cardapp/assets/avatar.png")

    register.apply_register()

    e = driver.find_element(By.CSS_SELECTOR, "body > section > div")
    assert "Mật khẩu không khớp" in e.text
    driver.save_screenshot(
        r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\register_not_match_password.png")