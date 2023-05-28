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
# 图像识别
import easyocr

data = 'trojan://29645da0-a43a-4ec4-95a1-57eb5e92be44@kr1.microsoft-orgwly.vip:443?allowInsecure=1#%E9%9F%A9%E5%9B%BD-1.04MB%2Fs%28Youtube%3A%E4%B8%8D%E8%89%AF%E6%9E%97%29'
sub_res = requests.get(f'https://sub.xeton.dev/sub?target=quanx&url={parse.quote(data)}&insert=false')
sub_res_list: list[str] = sub_res.text.split('\n')
for index,subitem in enumerate(sub_res_list):
        if subitem == '[server_local]' and sub_res_list[index+1] not in ['','[filter_local]']:
            # 有效qx订阅节点
            pass










# windows下需要先下载模型文件  https://blog.csdn.net/Loliykon/article/details/114334699
reader = easyocr.Reader(['ch_sim','en'],model_storage_directory='ocr_models')

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

youtube_nodes:list[str] = []

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

youtube_log = []

logging.info(f'===========================================================================开始获取节点信息...')
for index in range(100):
    subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g qmRkvKo-KbQ | head -n 1)" -vframes 1 dist/last.jpg',shell=True)
    sleep(2)
    try:
        youtube_log.append(f'=====================================节点:{index+1}信息======================================================')
        # 处理生成的二维码 生成节点信息
        data:str = qr_recognize(f'dist/last.jpg')
        logging.info(f'===============================================================================raw_data: {data}')
        ocr_result = reader.readtext('dist/last.jpg')
        logging.info(f'===============================================================================OCR: {ocr_result}')     # type: ignore
    except Exception as err:
        logging.error(f'==============================={err}==============================================')
    sub_res = requests.get(f'https://sub.xeton.dev/sub?target=quanx&url={parse.quote(data)}&insert=false')
    sub_res_list: list[str] = sub_res.text.split('\n')
    for index,subitem in enumerate(sub_res_list):
        try:
            if subitem == '[server_local]' and sub_res_list[index+1] not in ['','[filter_local]']:
                # 有效qx订阅节点
                # 添加到目标节点中
                youtube_nodes.append(sub_res_list[index+1])
                # 去重
                youtube_nodes = list(set(youtube_nodes))
                logging.info(f'==============================================================================当前节点池有: {len(youtube_nodes)}个节点')
        except:
            continue
    # 如果youtube_nodes和ocr_result[12][1]节点数量大于或相同则爬取结束
    try:
        if len(youtube_nodes)>=(int(ocr_result[12][1].split(':')[1])): # type: ignore
            break
    except:
        pass
    sleep(20)

open('dist/youtube.log','w+').write('\n'.join(youtube_log))
open('dist/youtube.list','w+').write('\n'.join(youtube_nodes))
logging.info(f'=========================================================================节点更新完成!')