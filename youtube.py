#!/usr/local/bin/python
# coding=utf-8
import requests
from myselenium.my_selenium import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
time.sleep(5)

open('dist/page_source.txt','w+',encoding="UTF-8").write(driver.page_source)
# logging.info(driver.page_source)

driver.save_screenshot('dist/pre_res.png')

# 模拟点击播放youtube
# element = driver.find_element(By.CLASS_NAME, 'ytp-play-button')
# element.click()
# ActionChains(driver).move_to_element(element).click().perform()

WebDriverWait(driver, 1000000).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ytp-play-button'))).click()


time.sleep(5)

driver.save_screenshot('dist/post_res.png')