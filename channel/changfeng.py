# 长风频道
from my_global import logging
from my_global import local
from my_global import reader
import copy
import datetime
import subprocess
from time import sleep
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from myselenium import my_selenium
from subconverter.converter import get_tag
from subconverter.converter import tag
import platform
import sys

if local:
    NEED_SAVE = False
else:
    if sys.argv[3] in ['true','TRUE','1','True']:
        NEED_SAVE = True
    elif sys.argv[3] in ['false','FALSE','0','False']:
        NEED_SAVE = False
    else:
        NEED_SAVE = False

def changfeng_func(channel_id:str):
    """长风的频道处理逻辑

    Args:
        channel_id (str): _description_
    """    
    raw_list = []
    ss_ssr_list = []
    vmess_trojan_list = []
    other_list = []
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
                    # lower()防止OCR识别成了大写
                    free_node_secret:str = ocr_result[index+1][1].lower() # type: ignore
                    break
        except Exception as e:
            logging.error(f'==============================================长风密码获取失败: {e}!!')    
            return []
        if free_node_secret and len(free_node_secret) > 0:
            if not NEED_SAVE:
                logging.info(f'==============================================长风密码:{free_node_secret}获取成功!')    
            else:
                logging.info(f'==============================================长风密码获取成功!')    
        else:
            logging.error(f'==============================================长风密码获取失败!!')    
            return []
        # 2. 访问目标网站
        driver = my_selenium.get_driver(headless=True)
        driver.get('https://v2rayse.com/free-node')
        sleep(10)
        # 3. 获取密码输入框 输入密码
        try:
            password_ele = driver.find_element(By.ID,'input-200')
            password_ele.send_keys(free_node_secret)
            sleep(2)
        except Exception as e:
            logging.error(f'获取密码输入框 输入密码失败: {e}')
            return []
        # 4. 点击提交密码
        try:
            submit_ele = driver.find_element(By.XPATH,r'//*[@id="app"]/div/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[2]/div/button')
            # ActionChains(driver).move_to_element(submit_ele).click(submit_ele)
            submit_ele.click()
            sleep(10)
        except Exception as e:
            logging.error(f'点击提交密码失败: {e}')
            return []
        # 5. 点击全选
        try:                                                          
            all_check_ele = driver.find_element(By.XPATH,r'/html/body/div/div/div/div/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[2]/div/div/div/span[1]/span')
            all_check_ele.click()
            sleep(2)
        except Exception as e:
            logging.error(f'点击全选失败: {e} , 请检查密码是否正确获取!')
            return []
        # 5. 点击复制
        try:
            cp_all_ele = driver.find_element(By.XPATH,r'/html/body/div/div/div/div/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[2]/div/div/div/span[3]/span')
            cp_all_ele.click()
            sleep(2)
        except Exception as e:
            logging.error(f'点击复制: {e}')
            return []
        
        # 获取粘贴板内容 
        # `````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
        ele = driver.find_element(By.XPATH, f'//*[@id="wl-edit"]')
        ac = ActionChains(driver)  # 模拟键盘操作
        ac.move_to_element(ele).click().perform()
        if platform.system().lower() == 'windows': # type: ignore
            ac.key_down(Keys.CONTROL).send_keys('v').perform()
        elif platform.system().lower() == 'linux': # type: ignore
            ac.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('v').perform()
        elif platform.system().lower() == 'macOS':  # type: ignore
            ac.key_down(Keys.COMMAND).send_keys('v').perform()
        clipbord_content = driver.find_element(By.XPATH, f'//*[@id="wl-edit"]').get_attribute("value")  # 获取输入框内容
        if clipbord_content == '':
            logging.error(f'===================================粘贴板内容获取失败!')
            return []
        else:
            logging.info(f'===================================已获取粘贴板内容:{clipbord_content}!')
        raw_list = clipbord_content.split('\n')
        # # ``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````

        # 控制分页
        try:
            driver.execute_script('window.scrollBy(0,-5000)')
            page_ele = driver.find_element(By.XPATH,r'/html/body/div/div/div/div/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div')
            page_ele.click()
            sleep(2)
        except Exception as e:
            logging.error(f'控制分页失败:{e}')
            return []
        # 控制下拉框全部
        try:
            all_page_ele = driver.find_element(By.XPATH,r'/html/body/div/div/div/div[2]/div/div[4]/div/div')
            all_page_ele.click()
            sleep(2)
        except Exception as e:  
            logging.error('控制下拉框全部失败')
            return []
        
        # 获取节点速度
        try:
            for index,proxy in enumerate(raw_list): # type: ignore
                if proxy.startswith(('ss','ssr')):
                    ss_ssr_list.append(proxy)
                    continue
                elif proxy.startswith(('vmess','trojan')):
                    vmess_trojan_list.append(proxy)
                else:
                    other_list.append(proxy)
                raw_tag = get_tag(proxy)
                if raw_tag.__contains__('美国'):
                    raw_tag = '美国'
                elif raw_tag.__contains__('印度'):
                    raw_tag = '印度'
                elif raw_tag.__contains__('英国'):
                    raw_tag = '英国'
                elif raw_tag.__contains__('澳大利亚'):
                    raw_tag =  '澳大利亚'
                elif raw_tag.__contains__('荷兰'):
                    raw_tag =  '荷兰'
                elif raw_tag.__contains__('乌克兰'):
                    raw_tag =  '乌克兰'
                elif raw_tag.__contains__('以色列'):
                    raw_tag =  '以色列'
                elif raw_tag.__contains__('印度尼西亚'):
                    raw_tag =  '印度尼西亚'
                elif raw_tag.__contains__('俄罗斯'):
                    raw_tag =  '俄罗斯'
                elif raw_tag.__contains__('德国'):
                    raw_tag =  '德国'
                elif raw_tag.__contains__('法国'):
                    raw_tag =  '法国'
                # 速度元素
                speed_ele = driver.find_element(By.XPATH,rf'//*[@id="app"]/div[1]/main/div/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[3]/div[1]/table/tbody/tr[{index+1}]/td[4]')
                # 速度
                speed = speed_ele.text
                result.append(tag(proxy,f'{raw_tag}-{speed}')) # type: ignore
            pass
        except Exception as e:
            logging.error(f'获取节点速度失败!: {e}')
            return []

        result = copy.deepcopy(sorted(set(result),key=result.index))
        # 节点排序
        logging.info(f'===========================================================================长风节点信息获取完毕,共获取有效数据源: [ss/ssr: {len(ss_ssr_list)}个,vmess/trojan: {len(vmess_trojan_list)}个,其他协议节点: {len(other_list)}个]')
        logging.info(f'')
        logging.info(f'')
        logging.info(f'')
        logging.info(f'')
        return result
    except Exception as err:
        logging.error(f'==============================={err}==============================================')
        return []