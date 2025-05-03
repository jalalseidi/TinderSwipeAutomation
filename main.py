import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
FB_EMAIL = os.getenv('FB_EMAIL')
FB_PASSWORD = os.getenv('FB_PASSWORD')

if not FB_EMAIL or not FB_PASSWORD:
    raise Exception("Environment variables FB_EMAIL and FB_PASSWORD must be set.")

def setup_driver():
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1,  # Auto-allow location
        "profile.default_content_setting_values.notifications": 1
    })
    return webdriver.Chrome(options=options)


def spoof_location(driver, latitude, longitude, accuracy=100):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy": accuracy
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)


def accept_cookies(driver, wait):
    try:
        cookies = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[2]/div/div/div[1]/button')))
        cookies.click()
        logging.info("Cookies accepted.")
    except TimeoutException:
        logging.warning("Cookies popup not found.")


def click_allow(driver, wait):
    try:
        allow_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Allow"]')))
        allow_button.click()
        logging.info('"Allow" clicked.')
    except TimeoutException:
        logging.warning('"Allow" button not found or already clicked.')

def click_login(driver, wait):
    try:
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Log in']")))
        login_button.click()
        logging.info("Login button clicked.")
    except TimeoutException:
        logging.error("Login button not found.")

def click_facebook_login(driver, wait):
    try:
        fb_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Log in with Facebook"]')))
        fb_login_button.click()
        logging.info("Facebook login clicked.")
        return True
    except TimeoutException:
        logging.error("Facebook login button not found.")
        return False

def switch_to_facebook_popup(driver):
    base_window = driver.current_window_handle
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    for handle in driver.window_handles:
        if handle != base_window:
            driver.switch_to.window(handle)
            logging.info("Switched to Facebook login popup.")
            return base_window
    raise Exception("Facebook popup window not found.")

def submit_facebook_login(driver):
    try:
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        password_field = driver.find_element(By.NAME, 'pass')
        login_button = driver.find_element(By.NAME, 'login')

        email_field.send_keys(FB_EMAIL)
        password_field.send_keys(FB_PASSWORD)
        login_button.click()
        logging.info("Facebook credentials submitted.")
    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Failed to fill Facebook login form: {e}")

def continue_as_user(driver, wait):
    try:
        continue_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//button[contains(text(), "Continue as")]'
        )))
        continue_button.click()
        logging.info("Clicked 'Continue as...'")
    except TimeoutException:
        logging.warning("'Continue as...' button not found — maybe login auto-continued.")

def verify_login_success(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Account"]')))
        logging.info("Login successful!")
    except TimeoutException:
        logging.error("Login failed or timed out.")

def allow_location(driver, wait):
    try:
        location_allow = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "lxn9zzn") and text()="Allow"]')))
        location_allow.click()
        logging.info("Location permission allowed.")
    except TimeoutException:
        logging.warning("Location permission popup not found.")

def allow_notification(driver, wait):
    try:
        notify_allow = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "lxn9zzn") and text()="I’ll miss out"]')))
        notify_allow.click()
        logging.info("Notification allowed.")
    except TimeoutException:
        logging.warning("Notification popup not found.")

def allow_cookies(driver, wait):
    try:
        cookie_allow = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "lxn9zzn") and text()="I accept"]')))
        cookie_allow.click()
        logging.info("Cookies allowed.")
    except TimeoutException:
        logging.warning("Cookies popup not found.")

def main():
    driver = setup_driver()

    spoof_location(driver, latitude=37.7749, longitude=-122.4194)  # Example: San Francisco

    wait = WebDriverWait(driver, 10)
    driver.get("https://tinder.com")

    try:
        accept_cookies(driver, wait)
        click_allow(driver, wait)
        click_login(driver, wait)
        if click_facebook_login(driver, wait):
            base_window = switch_to_facebook_popup(driver)
            submit_facebook_login(driver)
            continue_as_user(driver, wait)
            driver.switch_to.window(base_window)
            allow_location(driver, wait)
            allow_notification(driver, wait)
            allow_cookies(driver, wait)
            verify_login_success(driver)
    finally:
        input("Press ENTER to quit the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
