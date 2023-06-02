# 长风频道
from my_global import logging
from my_global import local
from my_global import reader
from my_global import qr_recognize
import copy
import datetime
import subprocess
from time import sleep
import pyperclip
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from myselenium import my_selenium
from subconverter.converter import get_tag
from subconverter.converter import tag
from subconverter.converter import sort_func

def changfeng_func(channel_id:str):
    """长风的频道处理逻辑

    Args:
        channel_id (str): _description_
    """    
    raw_list = []
    result = []
    logging.info(f'===========================================================================开始获取长风节点信息...')
    if not local:
        # 隔一段时间获取二维码 pyenv3.8 && ffmpeg -y -i "$(yt-dlp -g N1Qyg0scz7g | head -n 1)" -vframes 1 changfeng.jpg
        subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {channel_id} | head -n 1)" -vframes 1 dist/changfeng.jpg',shell=True)
        sleep(1)
    try:
        logging.info(f'====================================={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--节点信息======================================================')
        if local:
            ocr_result = reader.readtext('dist/local/changfeng.jpg')
        else:
            ocr_result = reader.readtext('dist/changfeng.jpg')
        # additional handling to ocr result... 
        logging.info(f'===============================================================================OCR: {ocr_result}')
        # 1. 获取密码: free_node_secret
        free_node_secret = ''
        try:
            for index,item in enumerate(ocr_result):
                if index>8 and (item[1].__contains__('V2rayse') or item[1].__contains__('VZrayse') or item[1].__contains__('comlfree') or item[1].__contains__('free-node')) and len(item[1])>=19: # type: ignore
                    free_node_secret:str = ocr_result[index+1][1] # type: ignore
                    break
        except Exception as e:
            logging.error(f'==============================================长风密码获取失败: {e}!!')    
            raise Exception(f'密码获取失败!:{e}')
        if free_node_secret and len(free_node_secret) == 6:
            logging.info(f'==============================================长风密码获取成功!')    
        else:
            logging.error(f'==============================================长风密码获取失败!!')    
            raise Exception('密码获取失败!')
        # 2. 访问目标网站
        driver = my_selenium.get_driver()
        driver.get('https://v2rayse.com/free-node')
        sleep(5)
        # 3. 获取密码输入框 输入密码
        try:
            password_ele = driver.find_element(By.ID,'input-200')
            password_ele.send_keys(free_node_secret)
            sleep(2)
        except Exception as e:
            logging.error(f'获取密码输入框 输入密码失败: {e}')
            raise e
        # 4. 点击提交密码
        try:
            submit_ele = driver.find_element(By.XPATH,r'//*[@id="app"]/div/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[2]/div/button')
            # ActionChains(driver).move_to_element(submit_ele).click(submit_ele)
            submit_ele.click()
            sleep(5)
        except Exception as e:
            logging.error(f'点击提交密码失败: {e}')
            raise e
        # 5. 点击全选
        try:
            all_check_ele = driver.find_element(By.XPATH,r'//*[@id="app"]/div[1]/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[2]/div/div/div/span[1]/span')
            all_check_ele.click()
            sleep(2)
        except Exception as e:
            logging.error(f'点击全选失败: {e}')
            raise e
        # 6. 点击复制
        try:
            copy_ele = driver.find_element(By.XPATH,r'//*[@id="app"]/div[1]/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[2]/div/div/div/span[3]/span')
            copy_ele.click()
            sleep(2)
        except Exception as e:
            logging.error(f'点击复制失败: {e}')
            raise e
        sub = pyperclip.paste()
        if not sub:
            logging.error('粘贴板内容为空!订阅获取失败')
            raise Exception('粘贴板内容为空!订阅获取失败')
        raw_list = sub.split('\r\n')

        # 控制分页
        try:
            page_ele = driver.find_element(By.XPATH,r'//*[@id="app"]/div[1]/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/i')
            page_ele.click()
            sleep(2)
        except Exception as e:
            logging.error('控制分页失败')
            raise Exception('控制分页失败')
        # 全选
        try:
            all_page_ele = driver.find_element(By.XPATH,r'/html/body/div/div/div/div[2]/div/div[4]/div/div')
            all_page_ele.click()
            sleep(2)
        except Exception as e:  
            logging.error('控制分页失败')
            raise Exception('控制分页失败')
        # 获取节点速度
        try:
            for index,proxy in enumerate(raw_list): # type: ignore
                if proxy.startswith(('ss','ssr')):
                    continue
                raw_tag = get_tag(proxy)
                # 速度元素
                speed_ele = driver.find_element(By.XPATH,rf'//*[@id="app"]/div[1]/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[3]/div[1]/table/tbody/tr[{index+1}]/td[4]')
                # 速度
                speed = speed_ele.text
                result.append(tag(proxy,f'{raw_tag}-{speed}')) # type: ignore
            pass
        except Exception as e:
            logging.error(f'获取节点速度失败!: {e}')
            raise Exception(f'获取节点速度失败!: {e}')

        result = copy.deepcopy(sorted(set(result),key=result.index))
        # 节点排序

        logging.info(f'=========================已抓取数据源: {len(result)}个')
    except Exception as err:
        logging.error(f'==============================={err}==============================================')

    logging.info(f'===========================================================================长风节点信息获取完毕,共获取有效数据源:{len(result)}个')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')