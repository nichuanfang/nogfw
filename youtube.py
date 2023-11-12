#!/usr/local/bin/python
# coding=utf-8
import re
from my_global import local
from my_global import logging
from channel import bulianglin
from channel import mac2win
from channel import changfeng
import time
import datetime
import random
from subconverter import converter
import concurrent.futures
import requests

live_pattern = re.compile(r'https://i.ytimg.com/vi/(.*?)/hqdefault_live.jpg')

def  live_streaming_id(youtuber:str):
    """通过youtuber油管主名称获取直播间id

    Args:
        youtuber (str): _description_
    """ 
    response = requests.get(f'https://www.youtube.com/@{youtuber}')
    # 获取直播间id
    if response.status_code == 200:
        html = response.text
        # 正则查找youtube直播间id
        try:
            live_id = live_pattern.findall(html)[0]
            return live_id
        except:
            # 不存在直播间
            return None

def batch_craw(channels:dict[str,dict]):
    """批量爬取频道的订阅

    Args:
        number (int): 爬取次数
        channels (dict): 爬取的频道列表
        sleeptime (int): 每次爬取后的休眠时间 单位:秒(s)

    Returns:
        _type_: _description_
    """    
    raw_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for youtuber in channels:
            channel_handler = channels[youtuber]
            channel_id = channel_handler['channel_id']
            func = channel_handler['func']
            # 执行对应的操作
            concurrent.futures.Future()
            res = executor.submit(func,channel_id)
            to_do.append(res)
        # 并发执行 获取结果
        for future in concurrent.futures.as_completed(to_do):  # 并发执行
            raw_list = raw_list + future.result()

    return raw_list

if __name__ == '__main__':
    try:
        raw_list = batch_craw(
                              {
                                #   不良林
                                  'bulianglin': {
                                      'channel_id': f'{live_streaming_id("bulianglin")}',
                                      'func': bulianglin.bulianglin_func
                                  },
                                #   马克吐温
                                  'mac2win': {
                                      'channel_id': f'{live_streaming_id("mac2win")}',
                                      'func': mac2win.mac2win_func
                                  }
                                #   长风 (节点质量太差 已废弃)
                                  #'changfeng': {
                                    # 'channel_id':  f'{CHANGFENG_CHANNEL_ID}',
                                     #'func': changfeng.changfeng_func
                                 # }  
                              }
                            )
        # 有新的订阅才更新
        logging.info(f'==================================================总数据源:{len(raw_list)}个')
        if not len(raw_list)==0:
            
            # 生成qx专用订阅
            generate_ini = converter.generate_template_ini
            logging.info(f'=========================================================================生成qx配置文件...')
            generate_ini = converter.add_quanx(raw_list,generate_ini)
            logging.info(f'=========================================================================qx配置文件已生成!')
            print(generate_ini)
            # 生成clash配置文件
            logging.info(f'=========================================================================生成clash配置文件...')
            generate_ini = converter.add_clash(raw_list,generate_ini)
            logging.info(f'=========================================================================clash配置文件已生成!')

            # 生成v2ray订阅
            logging.info(f'=========================================================================生成v2ray配置文件...')
            generate_ini = converter.add_v2ray(raw_list,generate_ini)
            logging.info(f'=========================================================================v2ray配置文件已生成!')

            with open('dist/dist-version', 'r+') as f:
                dist_version = f.read()
            last_date = dist_version.rsplit('-', 1)[0]
            # 如果和今天超过一个月 更新
            if (datetime.datetime.now() - datetime.datetime.strptime(last_date, '%Y-%m-%d')).days >= 30:
                # 随机生成一个文件 保持仓库处于活跃
                open('dist/dist-version','w+').write(time.strftime("%Y-%m-%d",time.localtime(time.time()))+'-'+''.join \
                                                     (random.sample('-abcdefghigklmnopqrstuvwxyz1234567890',20)))
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')
            logging.info(f'=========================================================================节点更新完成!')
        else:
            logging.info(f'==================================================无新节点更新!')
    except Exception as e:
        raw_list = []
        logging.info(f'爬取yt频道出错:{e}')
