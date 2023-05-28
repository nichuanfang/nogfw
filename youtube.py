import requests
import my_selenium
from my_selenium import get_driver
from my_selenium import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
# 爬youtube只能用firefox!
driver = get_driver('firefox')
driver.get('https://www.youtube.com/')
# driver.maximize_window()
time.sleep(5)
driver.save_screenshot('res.png')
