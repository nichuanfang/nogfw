#!/usr/local/bin/python
# coding=utf-8
import lxml 
import os
from selenium import webdriver 
from selenium.webdriver.remote.webdriver import WebDriver
import random
import io
import sys
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# ip代理池 防止被屏蔽 很重要
proxy_arr = [
    '--proxy-server=http://183.237.47.54:9091'
]

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
  # 随机从代理池选一个代理  
proxy = random.choice(proxy_arr)
# 随机选取一个ua
google_chrome_ua:list = UserAgent().data_browsers['chrome']
firefox_chrome_ua = UserAgent().data_browsers['firefox']


def get_driver(type:str='google',headless:bool = True):
  """获取驱动 默认获取谷歌驱动

  Args:
      type (str): 驱动类型 google|firefox
  """  
  if type == 'google':
    ua = random.choice(google_chrome_ua)
    # 谷歌驱动设置
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    # 默认无头模式
    if headless:
      options.add_argument('--headless')
    options.add_argument("--window-size=1920x1080")
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
    options.add_argument('log-level=3')
    # 禁止打印日志
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    executable_path = '/opt/chromedriver/chromedriver'  
    driver = webdriver.Chrome(executable_path=executable_path,chrome_options=options)
    # 隐形等待20秒
    driver.implicitly_wait(20)
    # 绕过检测
    with open('myselenium/stealth.min.js', 'r') as f:
      js = f.read()
        # 调用函数在页面加载前执行脚本 
      driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
  elif type == 'firefox':
    ua = random.choice(firefox_chrome_ua)
    options = webdriver.FirefoxOptions()
    options.add_argument('--no-sandbox')
    # 默认无头浏览器
    if headless:
      options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920x1080")
    # 规避检测
    options.add_argument('--disable-blink-features')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-default-browser-check')
    # 设置User-Agent
    options.add_argument(f'user-agent={ua}')
    # 最大化
    options.add_argument('--start-maximized')
    # 禁用缓存
    options.add_argument("disable-cache")
    options.add_argument('disable-infobars')
    options.add_argument('--ignore-certificate-errors') 
    executable_path = '/opt/chromedriver/geckodriver'
    # service_log_path关闭geckodriver.log日志
    driver = webdriver.Firefox(executable_path=executable_path,options=options,log_path=os.devnull,service_log_path=os.devnull)
    # 隐形等待20秒
    driver.implicitly_wait(20)
  else:
    driver = WebDriver()
  return driver

def get_soup(url:str,driver_type:str='google'):
  """获取BeautifulSoup对象 lxml解析

  Args:
      url (str): _网址_
      driver_type: 驱动类型 google|firefox
  """  
  driver:WebDriver = get_driver(driver_type)
  driver.get(url)
  html = driver.page_source
  return BeautifulSoup(html,"lxml")


def get_frame_soup(url:str,frame_id:str,driver_type:str='google'):
  """获取BeautifulSoup对象 lxml解析 前端使用frame骨架

  Args:
      url (str): _网址_
      frame_id (str): frame的id
      driver_type(str): 驱动类型 google|firefox
  """  
  driver:WebDriver = get_driver(driver_type)
  driver.switch_to.frame(frame_id)
  driver.get(url)
  html = driver.page_source
  return BeautifulSoup(html,"lxml")