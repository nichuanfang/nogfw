# 不良林频道
from my_global import logging
from my_global import qr_recognize
from my_global import local
from my_global import ocr_utils
import copy
import subprocess
from time import sleep
import datetime
import re


reader = ocr_utils.get_reader(['ch_sim', 'en'])

def bulianglin_func(channel_id:str):
    """不良林的频道处理逻辑

    Args:
        channel_id (str): 频道id
        number(int): 爬取次数
        sleeptime(int): 间隔时间

    """  
    if channel_id == None:
        return []
    raw_list = []
    ss_ssr_list = []
    vmess_trojan_list = []
    other_list = []
    crawl_number = 0
    
    # 先生成截图 计算抓取次数
    try:
        if not local:
            # 隔一段时间获取二维码
            subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {channel_id} | head -n 1)" -vframes 1 dist/bulianglin.jpg',shell=True)
            sleep(1)
            ocr_result:list[str] = ocr_utils.read_text('dist/bulianglin.jpg',reader) # type: ignore
        if local:
            ocr_result:list[str] = ocr_utils.read_text('dist/local/bulianglin.jpg',reader) # type: ignore
        for ocr in ocr_result: # type: ignore
            if ocr.__contains__('当前节点数量'):
                # 提取数字
                crawl_number = int(re.findall(r"\d+",ocr)[0])
    except Exception as err:
        logging.error(f'==============================={err}==============================================')
    
    logging.info(f'===========================================================================开始获取不良林节点信息...')
    if  not local:
        crawl_number = 1
    for craw_index in range(crawl_number*2):
        logging.info(f'=====================================开始第{craw_index+1}/{crawl_number*2}轮抓取======================================================')
        if not local:
            # 隔一段时间获取二维码
            subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {channel_id} | head -n 1)" -vframes 1 dist/bulianglin.jpg',shell=True)
            sleep(1)
        try:
            logging.info(f'====================================={datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--节点信息======================================================')
            # 处理生成的二维码 生成节点信息
            if local:
                data:str = qr_recognize(f'dist/local/bulianglin.jpg')
            else:
                data:str = qr_recognize(f'dist/bulianglin.jpg')
            if data.startswith(('ss','ssr')):
                ss_ssr_list.append(f'bulianglin:{data}')
            elif data.startswith(('vmess','trojan')):
                vmess_trojan_list.append(f'bulianglin:{data}')
            else:
                other_list.append(f'bulianglin:{data}')
            raw_list.append(f'bulianglin:{data}')
            logging.info(f'==================================================================raw_data: {data}')
            raw_list = copy.deepcopy(sorted(set(raw_list),key=raw_list.index))
            ss_ssr_list = copy.deepcopy(sorted(set(ss_ssr_list),key=ss_ssr_list.index))
            vmess_trojan_list = copy.deepcopy(sorted(set(vmess_trojan_list),key=vmess_trojan_list.index))
            other_list = copy.deepcopy(sorted(set(other_list),key=other_list.index))
            logging.info(f'====================================已抓取数据源: [ ss/ssr节点:{len(ss_ssr_list)}个 vmess/trojan节点:{len(vmess_trojan_list)}个 其他协议节点: {len(other_list)}个 ]')
        except Exception as err:
            logging.error(f'==============================={err}==============================================')
        if craw_index != crawl_number*2-1:
            sleep(17)
        logging.info(f'')
        logging.info(f'')
        logging.info(f'')
        logging.info(f'')
    logging.info(f'===========================================================================不良林节点信息获取完毕,共获取有效数据源: [ss/ssr: {len(ss_ssr_list)}个,vmess/trojan: {len(vmess_trojan_list)}个,其他协议节点: {len(other_list)}个]')
    return raw_list