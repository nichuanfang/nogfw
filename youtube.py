#!/usr/local/bin/python
# coding=utf-8
import requests
from myselenium.my_selenium import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from myselenium.my_selenium import BeautifulSoup
import time
import logging
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

logging.basicConfig(level=logging.INFO)
# 爬youtube只能用firefox!
driver = get_driver('firefox')

driver.get('https://www.youtube.com/watch?v=qmRkvKo-KbQ')
driver.maximize_window()
time.sleep(10)

open('page_source','w+',encoding="UTF-8").write(driver.page_source)

# 模拟点击播放youtube
element = driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
ActionChains(driver).move_to_element(element).click().perform()

driver.save_screenshot('dist/res.png')