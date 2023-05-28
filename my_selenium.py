#!/usr/local/bin/python
# coding=utf-8
import lxml 
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import random
import io
import sys
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import logging

# 日志设置
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s" 
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# ip代理池 防止被屏蔽 很重要
proxy_arr = [
    '--proxy-server=http://183.237.47.54:9091'
]

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
  # 随机从代理池选一个代理  
proxy = random.choice(proxy_arr)
# 随机选取一个ua
chrome_ua:list = UserAgent().data_browsers['chrome']
ua = random.choice(chrome_ua)


# 谷歌驱动设置
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# 不用打开界面 无头浏览器
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
# 设置User-Agent
options.add_argument(f'user-agent={ua}')
# 添加代理 代理还是有问题 todo待解决
# options.add_argument(proxy)
# 规避检测
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension',False)
options.add_argument('--disable-blink-features')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-extensions')
options.add_argument('--no-default-browser-check')
# 避免某些网页出错
options.add_argument('--disable-gpu')
# 最大化
options.add_argument('--start-maximized')
# 无痕模式
options.add_argument('--incognito')
# 禁用缓存
options.add_argument("disable-cache")
options.add_argument('disable-infobars')
options.add_argument('--ignore-certificate-errors') 
# 日志级别 0:INFO  1:WARNING 2:LOG_ERROR 3:LOG_FATAL  default is 0
# options.add_argument('log-level=3')
# 禁止打印日志
options.add_experimental_option('excludeSwitches', ['enable-logging'])
executable_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=executable_path,chrome_options=options)
# 绕过检测
with open('/code/crawler/my_selenium/stealth.min.js', 'r') as f:
  js = f.read()
    # 调用函数在页面加载前执行脚本 
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
# 隐形等待20秒
driver.implicitly_wait(20)

def get_soup(url:str):
  """获取BeautifulSoup对象 lxml解析

  Args:
      url (str): _网址_
  """  
  driver.get(url)
  html = driver.page_source
  return BeautifulSoup(html,"lxml")


def get_frame_soup(url:str,frame_id:str):
  """获取BeautifulSoup对象 lxml解析 前端使用frame骨架

  Args:
      url (str): _网址_
      frame_id (str): frame的id
  """  
  driver.switch_to.frame(frame_id)
  driver.get(url)
  html = driver.page_source
  return BeautifulSoup(html,"lxml")