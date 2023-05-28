import requests
from my_selenium import get_driver
from selenium.webdriver.common.by import By
from my_selenium import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
# 爬youtube只能用firefox!
driver = get_driver('firefox')
driver.get('https://www.youtube.com/watch?v=qmRkvKo-KbQ')
driver.maximize_window()
time.sleep(5)
# 模拟点击播放youtube
driver.find_element(By.CSS_SELECTOR, ".ytp-play-button").click()
driver.save_screenshot('res.png')
driver.close()