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
from PIL import Image
from qrcode import constants
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
def craw(number:int,video_id:str,sleeptime:int):
    # 未去重 打好标签的节点列表
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
                    all_nodes.append(sub_res_list[index+1])
                    # 节点去重 利用字典去重
                    all_nodes = list(dict.fromkeys(all_nodes))
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

def resize(file):
    im = Image.open(file)
    reim=im.resize((640, 640))#宽*高

    reim.save(file,dpi=(300.0,300.0)) ##200.0,200.0分别为想要设定的dpi值

def get_group_proxy_index(proxies:list):
    for index,proxy in enumerate(proxies):
        if proxy not in ['🔰 节点选择','♻️ 自动选择','🎯 全球直连']:
            return index
    return -1

def handle_group_proxy(final_dict,count,index):
    final_dict['proxy-groups'][index]['proxies'][get_group_proxy_index(final_dict['proxy-groups'][index]['proxies'])] = f'[{count}] '+final_dict['proxy-groups'][index] \
                    ['proxies'][get_group_proxy_index(final_dict['proxy-groups'][index]['proxies'])].replace('(Youtube:不良林)','')
    
def filter_proxies(tag:str,proxies:list[str]):
    res = []
    for proxy in proxies:
        if tag == 'google':
            # 使用延迟低的节点 
            if bool(re.search(r'香港|Hong Kong|HK|hk|新加坡|Singapore|SG|sg|台湾|Taiwan|TW|tw|台北|日本|Japan|JP|jp|韩国|Korea|KR|kr',proxy)):
                res.append(proxy)
        elif tag == 'github':
            # 使用延迟低的节点 
            if bool(re.search(r'香港|Hong Kong|HK|hk|新加坡|Singapore|SG|sg|台湾|Taiwan|TW|tw|台北|日本|Japan|JP|jp|韩国|Korea|KR|kr',proxy)):
                res.append(proxy)
        elif tag == 'openai':
            # 使用美国节点 
            if bool(re.search(r'美国|United States|US|us',proxy)):
                res.append(proxy)
    # 如果没有就缺省🎯 全球直连
    if len(res) == 0:
        res.append('🎯 全球直连')
    return res

def direct_rulesets():
    unbreak_ruleset = requests.get('https://cdn.jsdelivr.net/gh/sve1r/Rules-For-Quantumult-X@develop/Rules/Services/Unbreak.list')
    china_ruleset = requests.get('https://raw.githubusercontent.com/sve1r/Rules-For-Quantumult-X/develop/Rules/Region/China.list')
    china_ip_ruleset = requests.get('https://raw.githubusercontent.com/sve1r/Rules-For-Quantumult-X/develop/Rules/Region/ChinaIP.list')

    unbreak_rules = unbreak_ruleset.text.split('\n')
    china_rules = china_ruleset.text.split('\n')
    china_ip_rules = china_ip_ruleset.text.split('\n')
    all_rules = unbreak_rules+china_rules+china_ip_rules
    final_rulesets = []
    for all_rule in all_rules:
        new_rule = all_rule.strip()
        if new_rule == '' or new_rule.startswith('#'):
            continue
        try:
            rule_list = new_rule.split(',')
        except:
            continue
        if len(rule_list) < 3:
            continue
        first = rule_list[0]
        second = rule_list[1]
        third = rule_list[2]
        if first == 'host' or first == 'HOST':
            if third == 'DIRECT' or third == 'direct':
                final_rulesets.append(','.join(['DOMAIN',second,'🎯 全球直连']))

        elif first == 'host-suffix' or first == 'HOST-SUFFIX':
            if third == 'DIRECT' or third == 'direct':
                final_rulesets.append(','.join(['DOMAIN-SUFFIX','🎯 全球直连']))

        elif first == 'host-keyword' or first == 'HOST-KEYWORD':
            final_rulesets.append(','.join(['DOMAIN-KEYWORD',second,'🎯 全球直连']))

        elif first == 'ip-cidr' or first == 'IP-CIDR':
            final_rulesets.append(','.join(['IP-CIDR',second,'🎯 全球直连']))

    return final_rulesets

def google_github_openai_ruleset():
    google_ruleset = requests.get('https://raw.githubusercontent.com/sve1r/Rules-For-Quantumult-X/develop/Rules/Services/Google.list')
    github_ruleset = requests.get('https://raw.githubusercontent.com/sve1r/Rules-For-Quantumult-X/develop/Rules/Services/Github.list')
    openai_ruleset = requests.get('https://raw.githubusercontent.com/sve1r/Rules-For-Quantumult-X/develop/Rules/Services/OpenAI.list')

    google_rules = google_ruleset.text.split('\n')
    github_rules = github_ruleset.text.split('\n')
    openai_rules = openai_ruleset.text.split('\n')
    all_rules = google_rules+github_rules+openai_rules

    final_rulesets = []
    for all_rule in all_rules:
        new_rule = all_rule.strip()
        if new_rule == '' or new_rule.startswith('#'):
            continue
        try:
            rule_list = new_rule.split(',')
        except:
            continue
        if len(rule_list) < 3:
            continue
        first = rule_list[0]
        second = rule_list[1]
        third = rule_list[2]
        if first == 'host' or first == 'HOST':
            if third == 'Google Domestic':
                final_rulesets.append(','.join(['DOMAIN',second,'🎯 全球直连']))
            else:
                final_rulesets.append(','.join(['DOMAIN',second,third]))
        elif first == 'host-suffix' or first == 'HOST-SUFFIX':
            if third == 'Google Domestic':
                final_rulesets.append(','.join(['DOMAIN-SUFFIX','🎯 全球直连']))
            else:
                final_rulesets.append(','.join(['DOMAIN-SUFFIX',second,third]))
        elif first == 'host-keyword' or first == 'HOST-KEYWORD':
            final_rulesets.append(','.join(['DOMAIN-KEYWORD',second,third]))
        elif first == 'ip-cidr' or first == 'IP-CIDR':
            final_rulesets.append(','.join(['IP-CIDR',second,third]))
    return final_rulesets

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
                final_dict['proxy-groups'][1]['interval'] = 600 # type: ignore
                # 剔除低延迟节点
                if not bool(re.search(r'香港|Hong Kong|HK|hk|新加坡|Singapore|SG|sg|台湾|Taiwan|TW|tw|台北|日本|Japan|JP|jp|韩国|Korea|KR|kr',final_dict['proxy-groups'][1]['proxies'][0])):
                    final_dict['proxy-groups'][1]['proxies'] = []
                else:
                    # 自动选择
                    handle_group_proxy(final_dict,count,1)
                proxy:dict= copy.deepcopy(data_dict['proxies'][0])
                final_dict['proxies'][0]['name'] = f'[{count}] ' + proxy['name'].replace('(Youtube:不良林)','')
                # 节点选择
                handle_group_proxy(final_dict,count,0)
                # 国外媒体
                handle_group_proxy(final_dict,count,2)
                # 微软服务
                handle_group_proxy(final_dict,count,4)
                # 电报信息
                handle_group_proxy(final_dict,count,5)
                # 苹果服务
                handle_group_proxy(final_dict,count,6)
                # 漏网之鱼
                handle_group_proxy(final_dict,count,9)
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
    if len(final_dict['proxy-groups'][1]['proxies'])==0:
        # 如果自动选择没用可用的节点 默认🎯 全球直连 防止clash客户端报错
        final_dict['proxy-groups'][1]['proxies'].append('🎯 全球直连')
    proxies = []

    def sort_func(proxy):
        # 获取测速结果
        match = re.search(r'\d+.\d+',proxy.split('-')[-1])
        if match is not None:
            if proxy.split('-')[-1].lower().__contains__('mb'):
                return float(match.group())*1000
            return float(match.group())
        return 0.0
    
    for p in final_dict['proxies']:
        # 按照测速结果排序(降序) 
        proxies.append(p['name'])
    proxies.sort(key=sort_func,reverse=True) # type: ignore
    proxy_groups:list = final_dict['proxy-groups']
    # clash策略组详细配置请查看 https://stash.wiki/proxy-protocols/proxy-groups
    # 添加自定义策略 高可用 Fallback
    proxy_groups.insert(2,{
        'name': '🤔 高可用',
        'type': 'fallback',
        'url': 'http://www.gstatic.com/generate_204',
        'interval': 43200,
        'proxies': proxies
    })
    final_dict['proxy-groups'][0]['proxies'].insert(1,'🤔 高可用')
    # 添加自定义策略  Google
    proxy_groups.insert(3,{
        'name': 'Google',
        'type': 'fallback',
        'url': 'http://www.gstatic.com/generate_204',
        'interval': 43200,
        'proxies': filter_proxies('google',proxies)
    })
    # 添加自定义策略  Github
    proxy_groups.insert(4,{
        'name': 'Github',
        'type': 'fallback',
        'url': 'http://www.gstatic.com/generate_204',
        'interval': 43200,
        'proxies': filter_proxies('github',proxies)
    })

    # 添加自定义策略  OpenAI
    proxy_groups.insert(5,{
        'name': 'OpenAI',
        'type': 'fallback',
        'url': 'http://www.gstatic.com/generate_204',
        'interval': 43200,
        'proxies': filter_proxies('openai',proxies)
    })

    rules:list[str] = final_dict['rules']
    # 添加自定义规则 在第一个`国外媒体`之前 添加自定义规则
    logging.info(f'======================添加自定义规则: Google Github OpenAI==========================================')
    flag = 0
    for index,rule in enumerate(rules):
        if rule.__contains__('国外媒体'):
            # 找到插入位置
            flag = index
            break
    rulesets = google_github_openai_ruleset()
    for rule_index,ruleset in enumerate(rulesets):
        rules.insert(flag+rule_index,ruleset)

    logging.info(f'======================添加自定义规则: 🎯 全球直连==========================================')
    # 针对性直连
    
    for rule_ in rules:
        if rule_.__contains__('全球直连'):
            try:
                rules.remove(rule_)
            except:
                continue
    logging.info(f'==========================================================添加自定义直连之前的rules: {rules}')
    direct_rules = direct_rulesets()
    for direct_rule in direct_rules:
        rules.append(direct_rule)
    return final_dict


if __name__ == '__main__':
    # 环境
    try:
        ENV = sys.argv[1]
    except:
        ENV = 'dev'
    if ENV == 'dev':
        CARW_NUMBER = 5
        NEED_SAVE = False
    elif ENV == 'prod':
        CARW_NUMBER = 150
        NEED_SAVE = True
    else:
        CARW_NUMBER = 5
        NEED_SAVE = False

    # sys.argv[1]): CRAW_NUMBER 抓取次数
    all_nodes = craw(CARW_NUMBER,'qmRkvKo-KbQ',10)
    # 对节点按照测速结果 从快到慢降速排序
    def qx_sort(node):
        # 获取测速结果
        match = re.search(r'\d+.\d+',node.split('-')[-1])
        if match is not None:
            if node.split('-')[-1].lower().__contains__('mb'):
                return float(match.group())*1000
            return float(match.group())
        return 0.0
    all_nodes.sort(key=qx_sort,reverse=True) # type: ignore
    # sorted_nodes = sort_nodes(all_nodes)
    taged_nodes = []
    # 节点更改tag
    for index,node in enumerate(all_nodes):
        new_node = None
        # 更改tag
        match = re.search(r'tag.+$',node)
        if match is not None:
            tag = match.group()
            new_tag = 'tag='+f'[{index+1}] '+tag.replace('(Youtube:不良林)','').split('=')[1]
            new_node = re.sub(r'tag.+$',new_tag,node)
        if new_node == None:
            continue
        taged_nodes.append(new_node)
    
    # 生成qx专用订阅
    if NEED_SAVE:
        open('dist/qx-sub','w+').write('\n'.join(taged_nodes))

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
        if NEED_SAVE:
            open('dist/sub', 'w+',encoding='utf-8').write(encoder.decode('utf-8'))
    except Exception as e:
        logging.error(f'================================通用订阅生成失败!:{e}==========================================')

    # 生成通用订阅二维码
    try:
        qr = qrcode.QRCode(version=40
                    ,error_correction=constants.ERROR_CORRECT_M,
                    box_size=15, border=4,
                    image_factory=None,
                    mask_pattern=None)
        # 自适应大小
        if not NEED_SAVE:
            qr.add_data('\n'.join(raw_list))
            img = qr.make_image()
            with open('dist/sub.jpg', 'wb') as qrc:
                img.save(qrc)
            # 调整分辨率
            resize('dist/sub.jpg')
    except Exception as e:
        logging.error(f'================================二维码生成失败!:{e}==========================================')
    
    try:
        clash_dict = generate_clash_config(raw_list,{})
        with open('dist/clash.yml', 'w+',encoding='utf-8') as file:
            if NEED_SAVE:
                file.write(yaml.dump(clash_dict, allow_unicode=True,default_flow_style=False,sort_keys=False))
    except Exception as e:
        logging.error(f'================================clash文件生成失败!:{e}==========================================')

    logging.info(f'=========================================================================clash配置文件已生成!')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'')
    logging.info(f'=========================================================================节点更新完成!')
