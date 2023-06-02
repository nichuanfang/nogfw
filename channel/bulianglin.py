# 不良林频道
from my_global import logging
from my_global import qr_recognize
from my_global import local
from my_global import reader
import copy
import datetime
import subprocess
from time import sleep
from datetime import datetime


def bulianglin_func(channel_id:str,number:int,sleeptime:int):
    """不良林的频道处理逻辑

    Args:
        channel_id (str): 频道id
        number(int): 爬取次数
        sleeptime(int): 间隔时间

    """  
    raw_list = []
    logging.info(f'===========================================================================开始获取不良林节点信息...')
    # 默认165
    for craw_index in range(number):
        logging.info(f'=====================================开始第{craw_index+1}/{number}轮抓取======================================================')
        if not local:
            # 隔一段时间获取二维码
            subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {channel_id} | head -n 1)" -vframes 1 dist/bulianglin.jpg',shell=True)
            sleep(1)
        try:
            logging.info(f'====================================={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--节点信息======================================================')
            # 处理生成的二维码 生成节点信息
            if local:
                data:str = qr_recognize(f'dist/local/bulianglin.jpg')
            else:
                data:str = qr_recognize(f'dist/bulianglin.jpg')
            raw_list.append(data)
            logging.info(f'==================================================================raw_data: {data}')
            if local:
                ocr_result = reader.readtext('dist/local/bulianglin.jpg')
            else:
                ocr_result = reader.readtext('dist/bulianglin.jpg')
            # additional handling to ocr result... 
            logging.info(f'===============================================================================OCR: {ocr_result}')

            raw_list = copy.deepcopy(sorted(set(raw_list),key=raw_list.index))
            logging.info(f'=========================已抓取数据源: {len(raw_list)}个')
        except Exception as err:
            logging.error(f'==============================={err}==============================================')
        if craw_index != number-1:
            sleep(sleeptime)
        logging.info(f'===========================================================================不良林节点信息获取完毕,共获取有效数据源:{len(raw_list)}个')
        logging.info(f'')
        logging.info(f'')
        logging.info(f'')
        logging.info(f'')
    return raw_list