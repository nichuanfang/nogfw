#!/usr/local/bin/python
# coding=utf-8
from time import sleep
import cv2
import requests
import logging
import io
from urllib import request, parse
import os
import sys
import subprocess
from datetime import datetime
# 图像识别
import easyocr
# windows下需要先下载模型文件  https://blog.csdn.net/Loliykon/article/details/114334699
reader = easyocr.Reader(['ch_sim','en'],model_storage_directory='ocr_models')

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

def qr_recognize(file_path:str):
    qrcode_filename = file_path
    qrcode_image = cv2.imread(qrcode_filename)
    qrCodeDetector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = qrCodeDetector.detectAndDecode(qrcode_image)
    return data

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

logging.basicConfig(level=logging.INFO)

# 隔一段时间获取二维码
# ffmpeg -i "$(yt-dlp -g qmRkvKo-KbQ | head -n 1)" -vframes 1 dist/last.jpg

def craw(number:int,video_ids:list[str],sleeptime:int,all_nodes:list[str]):
    logging.info(f'===========================================================================开始获取节点信息...')
    log_list = []
    count = 0
    for index in range(number):
        logging.info(f'==========================================================第{index+1}轮抓取======================================================')
        for video_id in video_ids:
            pass
            subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {video_id} | head -n 1)" -vframes 1 dist/last.jpg',shell=True)
            sleep(2)
            try:
                logging.info(f'====================================={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--节点信息--索引======================================================')
                log_list.append(f'====================================={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--节点信息======================================================')
                # 处理生成的二维码 生成节点信息
                data:str = qr_recognize(f'dist/last.jpg')
                logging.info(f'===============================================================================raw_data: {data}')
                log_list.append(f'===============================================================================raw_data: {data}')
                ocr_result = reader.readtext('dist/last.jpg')
                logging.info(f'===============================================================================OCR: {ocr_result}')
                log_list.append(f'===============================================================================OCR: {ocr_result}')     # type: ignore
            except Exception as err:
                data = ''
                logging.error(f'==============================={err}==============================================')
            sub_res = requests.get(f'https://sub.xeton.dev/sub?target=quanx&url={parse.quote(data)}&insert=false')
            sub_res_list: list[str] = sub_res.text.split('\n')
            for index,subitem in enumerate(sub_res_list):
                try:
                    if subitem == '[server_local]' and sub_res_list[index+1] not in ['','[filter_local]']:
                        # 有效qx订阅节点
                        # 添加到目标节点中
                        all_nodes.append(sub_res_list[index+1])
                        # 去重
                        all_nodes = list(set(all_nodes))
                        logging.info(f'==============================================================================当前节点池有: {len(all_nodes)}个节点')
                except:
                    continue
        for node in all_nodes:
            if node.__contains__('不良林'):
                count+=1
        if count>=30 or len(all_nodes) >= 80:
            break
        sleep(sleeptime)
    return log_list

if __name__ == '__main__':
    all_nodes:list[str] = []
    youtube_log = craw(100,['qmRkvKo-KbQ','N1Qyg0scz7g','aG7DcQhlu7I'],10,all_nodes)
    open('dist/youtube.log','w+').write('\n'.join(youtube_log))
    open('dist/youtube.list','w+').write('\n'.join(all_nodes))
    logging.info(f'=========================================================================节点更新完成!')
