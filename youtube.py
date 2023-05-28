import requests
import my_selenium
from my_selenium import driver
import time
import logging

logging.basicConfig(level=logging.INFO)

driver.get('https://www.google.com')
driver.maximize_window()
time.sleep(5)
driver.save_screenshot('res.png')
