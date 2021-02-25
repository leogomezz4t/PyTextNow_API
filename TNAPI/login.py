import selenium
from selenium import webdriver
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#Functions
try:
    def login(user, password, path=r"geckodriver.exe"):
    opts = Options()

    browser = Firefox(executable_path=path, options=opts)

    browser.get('https://www.textnow.com/login')

    wait = WebDriverWait(browser, 500)

    user_elem = browser.find_element_by_id('txt-username')
    pass_elem = browser.find_element_by_id('txt-password')
    btn = browser.find_element_by_id('btn-login')

    user_elem.send_keys(user)
    pass_elem.send_keys(password)
    btn.click()

    wait.until(EC.url_matches('https://www.textnow.com/messaging'))
    wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, 'modal')))
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.chat-preview__contact-name')))
    time.sleep(3)
    sid = browser.get_cookie("connect.sid")["value"]
    browser.close()
    return sid
elif webdriver == 'chrome':
    def login(user, password, path=r"chromedriver.exe"):
    opts = Options()

    browser = Chrome(executable_path=path, options=opts)

    browser.get('https://www.textnow.com/login')

    wait = WebDriverWait(browser, 500)

    user_elem = browser.find_element_by_id('txt-username')
    pass_elem = browser.find_element_by_id('txt-password')
    btn = browser.find_element_by_id('btn-login')

    user_elem.send_keys(user)
    pass_elem.send_keys(password)
    btn.click()

    wait.until(EC.url_matches('https://www.textnow.com/messaging'))
    wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, 'modal')))
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.chat-preview__contact-name')))
    time.sleep(3)
    sid = browser.get_cookie("connect.sid")["value"]
    browser.close()
    return sid
