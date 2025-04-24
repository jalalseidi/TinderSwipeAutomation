from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

driver = webdriver.Chrome()
driver.get("https://tinder.com")
sleep(3)

# Try accepting cookies
try:
    allow_location_button = driver.find_element(By.XPATH,
                                                value='//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')
    allow_location_button.click()

    notifications_button = driver.find_element(By.XPATH,
                                               value='//*[@id="modal-manager"]/div/div/div/div/div[3]/button[2]')
    notifications_button.click()

    cookies = driver.find_element(By.XPATH, value='//*[@id="content"]/div/div[2]/div/div/div[1]/button')
    cookies.click()
    print("popup clicked.")
except:
    print("No cookie popup appeared or couldn't click.")


# Try clicking Log in
try:
    login_button = driver.find_element(By.XPATH, "//*[text()='Log in']")
    login_button.click()
    print("Login button clicked.")
except:
    print("Login button not found.")

input("Press ENTER to quit the browser...")  # ⬅️ Keeps browser open
driver.quit()
