import requests
import my_selenium
from my_selenium import driver
import time
import logging

logging.basicConfig(level=logging.INFO)

driver.get('https://www.youtube.com/watch?v=qmRkvKo-KbQ')
driver.maximize_window()
time.sleep(5)
driver.get_screenshot_as_file('test.png')
