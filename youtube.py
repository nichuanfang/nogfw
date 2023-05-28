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
logging.basicConfig(level=logging.INFO)

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

logging.info(f'开始获取节点信息...')
for index in range(1):
    subprocess.call(f'ffmpeg -i "$(yt-dlp -g qmRkvKo-KbQ | head -n 1)" -vframes 1 dist/last.jpg',shell=True)
    try:
        # 处理生成的二维码 生成节点信息
        data:str = qr_recognize(f'dist/last.jpg')
    except:
        subprocess.call(f'ffmpeg -i "$(yt-dlp -g qmRkvKo-KbQ | head -n 1)" -vframes 1 dist/last.jpg',shell=True)
        data:str = qr_recognize(f'dist/last.jpg')
    logging.info(f'已获取到节点: {data}')
    sub_res = requests.get(f'https://sub.xeton.dev/sub?target=quanx&url={parse.quote(data)}&insert=false')
    sub_res_list: list[str] = sub_res.text.split('\n')
    for index,subitem in enumerate(sub_res_list):
        try:
            if subitem == '[server_local]' and sub_res_list[index+1].startswith(('shadowsocks ','vmess','trojan','socks5','http')):
                # 添加到目标节点中
                youtube_nodes.append(sub_res_list[index+1])
                # 去重
                youtube_nodes = list(set(youtube_nodes))
        except:
            continue
    sleep(30)

open('dist/youtube.list','w+').write('\n'.join(youtube_nodes))
os.remove(f'dist/last.jpg')
logging.info(f'节点更新完成!')