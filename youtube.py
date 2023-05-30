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
import json
import yaml
import copy
import re
import qrcode
from qrcode import constants
# 图像识别
import easyocr

data = ['🔰 节点选择','♻️ 自动选择','🎯 全球直连','🇺🇲 美国-4.03MB/s(Youtube:不良林)']
data[-1] = '[1] '+data[-1].replace('(Youtube:不良林)','')

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
def craw(number:int,video_id:str,sleeptime:int):
    all_nodes = []
    logging.info(f'===========================================================================开始获取节点信息...')
    count = 1
    # 默认130
    for craw_index in range(number):
        logging.info(f'=====================================开始第{craw_index+1}/{number}轮抓取======================================================')
        # 隔一段时间获取二维码
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
            # additional handling to ocr result... 
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
                    node = sub_res_list[index+1]
                    new_node = None
                    # 更改tag
                    match = re.search(r'tag.+$',node)
                    if match is not None:
                        tag = match.group()
                        new_tag = 'tag='+f'[{count}] '+tag.replace('(Youtube:不良林)','').split('=')[1]
                        new_node = re.sub(r'tag.+$',new_tag,node)
                    if new_node == None:
                        continue
                    all_nodes.append(new_node)
                    count+=1
                    # 去重list(set(all_nodes))
                    all_nodes = sorted(set(all_nodes),key=all_nodes.index)
                    logging.info(f'==============================================================================当前节点池有: {len(all_nodes)}个节点')
                    logging.info(f'')
                    logging.info(f'')
                    logging.info(f'')
                    logging.info(f'')
            except:
                continue
        if craw_index != number-1:
            sleep(sleeptime)
    return all_nodes


def generate_clash_config(raw_list:list,final_dict:dict): # type: ignore
    count = 1
    for index,raw in enumerate(raw_list):
        logging.info(f'handle raw:{raw}======================================')
        # sub_res = request.urlopen(f'https://sub.xeton.dev/sub?target=clash&url={parse.quote(raw)}&insert=false')
        sub_res = requests.get(f'https://sub.xeton.dev/sub?target=clash&url={parse.quote(raw)}&insert=false')
        # logging.info(f'订阅转换后的响应:状态码:{sub_res.status_code}  ok:{sub_res.ok}=====================================================')
        # logging.info(f'clash dict:{sub_res.text}======================================')
        if not sub_res.ok:
            continue
        try:
            data_dict:dict = yaml.load(sub_res.text, Loader=yaml.FullLoader)
            #logging.info(f'clash dict:{data_dict}======================================')
            if not final_dict:
                final_dict:dict = copy.deepcopy(data_dict)
                final_dict['socks-port'] = 10808 # type: ignore
                final_dict['port'] = 10809 # type: ignore
            #   #自动选择 多久检测一次速度 自动切换 单位s(秒)
                final_dict['proxy-groups'][1]['interval'] = 1800 # type: ignore
                # 剔除低延迟节点
                if not bool(re.search(r'香港|Hong Kong|HK|hk|新加坡|Singapore|SG|sg|台湾|Taiwan|TW|tw|台北|日本|Japan|JP|jp|韩国|Korea|KR|kr',final_dict['proxy-groups'][1]['proxies'][0])):
                    final_dict['proxy-groups'][1]['proxies'] = []
                else:
                    final_dict['proxy-groups'][1]['proxies'][-1] = f'[{count}] '+final_dict['proxy-groups'][1]['proxies'][-1].replace('(Youtube:不良林)','')
                proxy:dict= copy.deepcopy(data_dict['proxies'][0])
                final_dict['proxies'][0]['name'] = f'[{count}] ' + proxy['name'].replace('(Youtube:不良林)','')
                final_dict['proxy-groups'][2]['proxies'][-1] = f'[{count}] '+final_dict['proxy-groups'][2]['proxies'][-1].replace('(Youtube:不良林)','')
                final_dict['proxy-groups'][4]['proxies'][-1] = f'[{count}] '+final_dict['proxy-groups'][4]['proxies'][-1].replace('(Youtube:不良林)','')
                final_dict['proxy-groups'][5]['proxies'][-1] = f'[{count}] '+final_dict['proxy-groups'][5]['proxies'][-1].replace('(Youtube:不良林)','')
                final_dict['proxy-groups'][6]['proxies'][-1] = f'[{count}] '+final_dict['proxy-groups'][6]['proxies'][-1].replace('(Youtube:不良林)','')
                final_dict['proxy-groups'][9]['proxies'][-1] = f'[{count}] '+final_dict['proxy-groups'][9]['proxies'][-1].replace('(Youtube:不良林)','')
                count+=1
            else:
                # 添加节点
                proxy:dict= copy.deepcopy(data_dict['proxies'][0])

                proxy['name'] = f'[{count}] ' + proxy['name'].replace('(Youtube:不良林)','')

                final_dict['proxies'].append(proxy)

                # 分组配置

                # 节点选择
                final_dict['proxy-groups'][0]['proxies'].append(proxy['name']) # type: ignore
                # 自动选择

                # 正则匹配 排除延迟低的节点
                if bool(re.search(r'香港|Hong Kong|HK|hk|新加坡|Singapore|SG|sg|台湾|Taiwan|TW|tw|台北|日本|Japan|JP|jp|韩国|Korea|KR|kr',proxy['name'])):
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
                count+=1
        except Exception as e:
            logging.error(f'=========================================raw:{raw}转换为clash配置文件失败!: {e}')
    return final_dict


if __name__ == '__main__':
    # sys.argv[1]): CRAW_NUMBER 抓取次数
    all_nodes = craw(int(sys.argv[1]),'qmRkvKo-KbQ',10)
    # 生成qx专用订阅
    open('dist/qx-sub','w+').write('\n'.join(all_nodes))

    # 生成clash配置文件
    logging.info(f'=========================================================================生成clash配置文件...')

    # raw_list = ['vmess://eyJ2IjoiMiIsInBzIjoi576O5Zu9LTUuNjNNQi9zKFlvdXR1YmU65LiN6Imv5p6XKSIsImFkZCI6IjIzLjIyNC4xMTAuMTg0IiwicG9ydCI6IjQ0MyIsInR5cGUiOiJub25lIiwiaWQiOiI0MTgwNDhhZi1hMjkzLTRiOTktOWIwYy05OGNhMzU4MGRkMjQiLCJhaWQiOiI2NCIsIm5ldCI6IndzIiwicGF0aCI6Ii9wYXRoLzA4MDcxMjM0MjMxMCIsImhvc3QiOiIiLCJ0bHMiOiJ0bHMifQ==','vmess://eyJ2IjoiMiIsInBzIjoi576O5Zu9LTQuMzlNQi9zKFlvdXR1YmU65LiN6Imv5p6XKSIsImFkZCI6IjE5OC4yLjE5Ni40OSIsInBvcnQiOiI1NDQzNCIsInR5cGUiOiJub25lIiwiaWQiOiI0MTgwNDhhZi1hMjkzLTRiOTktOWIwYy05OGNhMzU4MGRkMjQiLCJhaWQiOiI2NCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6IiIsInRscyI6IiJ9']

    # raw数据去重
    raw_list = copy.deepcopy(sorted(set(raw_list),key=raw_list.index))
    # base64加密
    encoder = base64.b64encode(('\n'.join(raw_list)).encode("utf-8"))
    # 解码为 utf-8 字符串
    try:
        # 生成通用订阅
        open('dist/sub', 'w+',encoding='utf-8').write(encoder.decode('utf-8'))
    except Exception as e:
        logging.error(f'================================通用订阅生成失败!:{e}==========================================')

    # 生成通用订阅二维码
    try:
        img = qrcode.make('\n'.join(raw_list),version=None,
                    error_correction=constants.ERROR_CORRECT_M,
                    box_size=10, border=4,
                    image_factory=None,
                    mask_pattern=None)
        with open('dist/sub.jpg', 'wb') as qrc:
            img.save(qrc)
    except Exception as e:
        logging.error(f'================================二维码生成失败!:{e}==========================================')
    
    try:
        clash_dict = generate_clash_config(raw_list,{})
        with open('dist/clash.yml', 'w+',encoding='utf-8') as file:
            file.write(yaml.dump(clash_dict, allow_unicode=True,default_flow_style=False,sort_keys=False))
    except Exception as e:
        logging.error(f'================================clash文件生成失败!:{e}==========================================')

    logging.info(f'=========================================================================clash配置文件已生成!')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'=========================================================================节点更新完成!')
