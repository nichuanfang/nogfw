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

def wait_click(driver, class_name, delay = 20):
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        myElem.click()
        return myElem
    except RuntimeError:
        print("Loading took too much time!")


# 爬youtube只能用firefox!
driver = get_driver('firefox')
# https://www.youtube.com/watch?v=qmRkvKo-KbQ
driver.get('https://www.youtube.com/watch?v=dOfQX8lLcdc')
time.sleep(5)

open('dist/page_source.txt','w+',encoding="UTF-8").write(driver.page_source)
# logging.info(driver.page_source)

driver.save_screenshot('dist/pre_res.png')

# 模拟点击播放youtube
# element = driver.find_element(By.CLASS_NAME, 'ytp-play-button')
# element.click()
# ActionChains(driver).move_to_element(element).click().perform()

wait_click(driver,'ytp-play-button')
# wait_click(driver,'ytp-next-button')
# driver.refresh()
time.sleep(5)

driver.save_screenshot('dist/post_res.png')