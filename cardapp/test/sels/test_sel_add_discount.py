
from cardapp.test.sels.pages.AdminPage import AdminPage
from cardapp.test.sels.pages.LoginPage import LoginPage
from cardapp.test.test_base import driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def test_add_discount_success(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("admin", "123456")
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, "#admin-navbar-collapse > ul.nav.navbar-nav.mr-auto > li:nth-child(5) > a")
    e.click()
    time.sleep(2)

    create = driver.find_element(By.CSS_SELECTOR, "body > div.container > ul > li:nth-child(2) > a")
    create.click()
    time.sleep(2)

    discount_code = driver.find_element(By.NAME, "code")
    discount_code.send_keys("TESTCODE25")
    time.sleep(1)

    description = driver.find_element(By.ID, "description")
    description.send_keys("TEST DESCRIPTION")
    time.sleep(1)

    value = driver.find_element(By.NAME, "value")
    value.send_keys("25")
    time.sleep(1)
    driver.execute_script('window.scrollTo(0, 500)')
    time.sleep(1)

    end_date = driver.find_element(By.ID, "end_date")

    driver.execute_script(
        "arguments[0].value = '2027-04-16 21:19:00';",
        end_date
    )


    max_quantity = driver.find_element(By.NAME, "max_quantity")
    max_quantity.send_keys("5")
    time.sleep(1)


    save_button = driver.find_element(By.CSS_SELECTOR, "body > div.container > form > fieldset > div:nth-child(14) > div > input.btn.btn-primary")
    save_button.click()
    time.sleep(1)
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\add_discount_success.png")


def test_add_discount_with_existed_code(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("admin", "123456")
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, "#admin-navbar-collapse > ul.nav.navbar-nav.mr-auto > li:nth-child(5) > a")
    e.click()
    time.sleep(2)

    create = driver.find_element(By.CSS_SELECTOR, "body > div.container > ul > li:nth-child(2) > a")
    create.click()
    time.sleep(2)

    discount_code = driver.find_element(By.NAME, "code")
    discount_code.send_keys("TESTCODE25")
    time.sleep(1)

    description = driver.find_element(By.ID, "description")
    description.send_keys("TEST DESCRIPTION")
    time.sleep(1)

    value = driver.find_element(By.NAME, "value")
    value.send_keys("25")
    time.sleep(1)
    driver.execute_script('window.scrollTo(0, 500)')
    time.sleep(1)

    end_date = driver.find_element(By.ID, "end_date")

    driver.execute_script(
        "arguments[0].value = '2027-04-16 21:19:00';",
        end_date
    )


    max_quantity = driver.find_element(By.NAME, "max_quantity")
    max_quantity.send_keys("5")
    time.sleep(1)


    save_button = driver.find_element(By.CSS_SELECTOR, "body > div.container > form > fieldset > div:nth-child(14) > div > input.btn.btn-primary")
    save_button.click()
    time.sleep(1)
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\add_discount_with_existed_code.png")


def test_add_discount_with_invalid_end_date(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("admin", "123456")
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, "#admin-navbar-collapse > ul.nav.navbar-nav.mr-auto > li:nth-child(5) > a")
    e.click()
    time.sleep(2)

    create = driver.find_element(By.CSS_SELECTOR, "body > div.container > ul > li:nth-child(2) > a")
    create.click()
    time.sleep(2)

    discount_code = driver.find_element(By.NAME, "code")
    discount_code.send_keys("TESTCODE01")
    time.sleep(1)

    description = driver.find_element(By.ID, "description")
    description.send_keys("TEST DESCRIPTION")
    time.sleep(1)

    value = driver.find_element(By.NAME, "value")
    value.send_keys("51")
    time.sleep(1)
    driver.execute_script('window.scrollTo(0, 500)')
    time.sleep(1)

    end_date = driver.find_element(By.ID, "end_date")
    driver.execute_script(
        "arguments[0].value = '2025-04-16 21:19:00';",
        end_date
    )


    max_quantity = driver.find_element(By.NAME, "max_quantity")
    max_quantity.send_keys("5")
    time.sleep(1)


    save_button = driver.find_element(By.CSS_SELECTOR, "body > div.container > form > fieldset > div:nth-child(14) > div > input.btn.btn-primary")
    save_button.click()
    time.sleep(1)
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\add_discount_with_invalid_enddate.png")

def test_add_discount_with_invalid_min_max_quantity(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("admin", "123456")
    time.sleep(2)

    e = driver.find_element(By.CSS_SELECTOR, "#admin-navbar-collapse > ul.nav.navbar-nav.mr-auto > li:nth-child(5) > a")
    e.click()
    time.sleep(2)

    create = driver.find_element(By.CSS_SELECTOR, "body > div.container > ul > li:nth-child(2) > a")
    create.click()
    time.sleep(2)

    discount_code = driver.find_element(By.NAME, "code")
    discount_code.send_keys("TESTCODE055")
    time.sleep(1)

    description = driver.find_element(By.ID, "description")
    description.send_keys("TEST DESCRIPTION")
    time.sleep(1)

    value = driver.find_element(By.NAME, "value")
    value.send_keys("25")
    time.sleep(1)
    driver.execute_script('window.scrollTo(0, 500)')
    time.sleep(1)

    end_date = driver.find_element(By.ID, "end_date")
    driver.execute_script(
        "arguments[0].value = '2025-04-16 21:19:00';",
        end_date
    )


    min_quantity = driver.find_element(By.NAME, "min_quantity")
    min_quantity.send_keys("2")
    time.sleep(1)


    max_quantity = driver.find_element(By.NAME, "max_quantity")
    max_quantity.send_keys("1")
    time.sleep(1)


    save_button = driver.find_element(By.CSS_SELECTOR, "body > div.container > form > fieldset > div:nth-child(14) > div > input.btn.btn-primary")
    save_button.click()
    time.sleep(1)
    driver.save_screenshot(r"D:\ProjectGithub\Card-Selling-System\cardapp\test\sels\ActualResult\add_discount_with_invalid_min_max_quantity.png")


