#!/usr/local/bin/python
# coding=utf-8
from time import sleep
import cv2
import requests
import logging
import io
from urllib import request, parse
import sys
import subprocess
from datetime import datetime
import os
import base64
import yaml
import json
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
raw_list = []
logging.basicConfig(level=logging.INFO)
def craw(video_id:str,sleeptime:int):
    all_nodes = []
    logging.info(f'===========================================================================开始获取节点信息...')
    # 首先确定节点池数量

    # 默认抓取60次
    number = 60
    subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {video_id} | head -n 1)" -vframes 1 dist/last.jpg',shell=True)
    while True:
        if not os.path.exists('dist/last.jpg'):
            logging.info(f'==========================================================等待截图生成...======================================================')
            sleep(1)
        else:
            break
    res = reader.readtext('dist/last.jpg')
    for parent_node in res: 
        for child in parent_node:
            if type(child)==str and child.__contains__('当前节点数量'):
                number = int(child.split(':')[1])
                logging.info(f'==========================================================共需抓取{number*2+5}轮======================================================')

    # 5次冗余时间 number*2+5
    for index in range(3):
        logging.info(f'==========================================================第{index+1}/{number*2+5}轮抓取======================================================')
        # 隔一段时间获取二维码
        if index != 0:
            subprocess.call(f'ffmpeg -y -i "$(yt-dlp -g {video_id} | head -n 1)" -vframes 1 dist/last.jpg',shell=True)
            while True:
                if not os.path.exists('dist/last.jpg'):
                    logging.info(f'==========================================================等待截图生成...======================================================')
                    sleep(1)
                else:
                    break
        try:
            logging.info(f'====================================={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--节点信息======================================================')
            # 处理生成的二维码 生成节点信息
            data:str = qr_recognize(f'dist/last.jpg')
            raw_list.append(data)
            logging.info(f'===============================================================================raw_data: {data}')
            ocr_result = reader.readtext('dist/last.jpg')
            logging.info(f'===============================================================================OCR: {ocr_result}')
        except Exception as err:
            data = ''
            all_nodes = []
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
                    logging.info(f'')
                    logging.info(f'')
                    logging.info(f'')
                    logging.info(f'')
            except:
                continue
        if index != (number*2+4):
            sleep(sleeptime)
    return all_nodes


def generate_clash_config(raw_list:list,final_dict:dict):
    for raw in raw_list:
        sub_res = requests.get(f'https://sub.xeton.dev/sub?target=clash&url={parse.quote(raw)}&insert=false')
        with open('dist/clash_temp.yml','w+',encoding='utf-8') as temp_file:
            temp_file.write(sub_res.text)
        with open('dist/clash_temp.yml','r+',encoding='utf-8') as f:
          try:
              data_dict:dict = yaml.load(f, Loader=yaml.FullLoader)
              if not final_dict:
                  final_dict:dict = data_dict
                  final_dict['socks-port'] = 10808 # type: ignore
                  final_dict['port'] = 10809 # type: ignore
                  #自动选择 多久检测一次速度 自动切换 单位s(秒)
                  final_dict['proxy-groups'][1]['interval'] = 3600 # type: ignore
              else:
                  # 添加节点
                  proxy:dict= data_dict['proxies'][0]
                  proxies:list = final_dict['proxies'] # type: ignore
                  proxies.append(proxy)
                  # 分组配置

                  # 节点选择
                  final_dict['proxy-groups'][0]['proxies'].append(proxy['name']) # type: ignore
                  # 自动选择
                  final_dict['proxy-groups'][1]['proxies'].append(proxy['name']) # type: ignore
                  # 国外媒体
                  final_dict['proxy-groups'][2]['proxies'].append(proxy['name']) # type: ignore
                  # 微软服务
                  final_dict['proxy-groups'][4]['proxies'].append(proxy['name']) # type: ignore
                  # 电报信息
                  final_dict['proxy-groups'][5]['proxies'].append(proxy['name']) # type: ignore
                  # 苹果服务
                  final_dict['proxy-groups'][6]['proxies'].append(proxy['name']) # type: ignore
                  # 漏网之鱼
                  final_dict['proxy-groups'][9]['proxies'].append(proxy['name']) # type: ignore
          except yaml.YAMLError as e:
              print(e)
        os.remove('dist/clash_temp.yml')
    return final_dict


if __name__ == '__main__':
    all_nodes = craw('qmRkvKo-KbQ',10)
    open('dist/youtube.list','w+').write('\n'.join(all_nodes))

    # 生成clash配置文件
    logging.info(f'=========================================================================生成clash配置文件...')
    # raw数据去重
    # raw_list = ['vmess://eyJ2IjoiMiIsInBzIjoi576O5Zu9LTUuNjNNQi9zKFlvdXR1YmU65LiN6Imv5p6XKSIsImFkZCI6IjIzLjIyNC4xMTAuMTg0IiwicG9ydCI6IjQ0MyIsInR5cGUiOiJub25lIiwiaWQiOiI0MTgwNDhhZi1hMjkzLTRiOTktOWIwYy05OGNhMzU4MGRkMjQiLCJhaWQiOiI2NCIsIm5ldCI6IndzIiwicGF0aCI6Ii9wYXRoLzA4MDcxMjM0MjMxMCIsImhvc3QiOiIiLCJ0bHMiOiJ0bHMifQ==','vmess://eyJ2IjoiMiIsInBzIjoi576O5Zu9LTQuMzlNQi9zKFlvdXR1YmU65LiN6Imv5p6XKSIsImFkZCI6IjE5OC4yLjE5Ni40OSIsInBvcnQiOiI1NDQzNCIsInR5cGUiOiJub25lIiwiaWQiOiI0MTgwNDhhZi1hMjkzLTRiOTktOWIwYy05OGNhMzU4MGRkMjQiLCJhaWQiOiI2NCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6IiIsInRscyI6IiJ9']
    raw_list = list(set(raw_list)) 
    clash_dict = generate_clash_config(raw_list,{})
    with open('dist/clash.yml', 'w+',encoding='utf-8') as file:
        file.write(yaml.dump(clash_dict, allow_unicode=True,default_flow_style=False,sort_keys=False))
    logging.info(f'=========================================================================clash配置文件已生成!')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'=========================================================================节点更新完成!')
