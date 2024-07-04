from selenium.webdriver.common.by import By


def check_exists_by_class_name(driver, xpath):
    try:
        driver.find_element(By.CLASS_NAME, xpath)
    except Exception:
        return False
    return True
