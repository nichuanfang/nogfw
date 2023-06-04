#!/usr/local/bin/python
# coding=utf-8
from my_global import local
from my_global import logging
from channel import bulianglin
from channel import changfeng
import time
import sys
import random
from subconverter import converter
import concurrent.futures

def batch_craw(number:int,channels:dict[str,dict],sleeptime:int):
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
            res = concurrent.futures.Future()
            if youtuber == 'bulianglin':
                res = executor.submit(func,channel_id,number,sleeptime)
            elif youtuber == 'changfeng':
                res = executor.submit(func,channel_id)
            else:
                pass
            to_do.append(res)
        # 并发执行 获取结果
        for future in concurrent.futures.as_completed(to_do):  # 并发执行
            raw_list = raw_list + future.result()

    return raw_list

if __name__ == '__main__':
    # 切换至本地开发模式 需手动将my_global的local改为True!
    # 切换至线上模式 需手动将my_global的local改为False!
    if local:
        CARW_NUMBER = 1
        CRAW_SLEEP_SECONDS = 10
        BULIANGLIN_CHANEL_ID = ''
        CHANGFENG_CHANNEL_ID = ''
    else:
        # 环境变量检测
        # 爬取次数
        assert sys.argv[1] != None and sys.argv[1] != ''
        # 爬取间隔(秒)
        assert sys.argv[2] != None and sys.argv[2] != ''
        # 不良林yt频道id
        assert sys.argv[3] != None and sys.argv[3] != ''
        # 长风yt频道id
        assert sys.argv[4] != None and sys.argv[4] != ''
        CARW_NUMBER = int(sys.argv[1])
        CRAW_SLEEP_SECONDS = int(sys.argv[2])
        # 不良林yt频道id
        BULIANGLIN_CHANEL_ID = sys.argv[3]
        # 长风yt频道id
        CHANGFENG_CHANNEL_ID = sys.argv[4]
    try:
        # 不良林
        # raw_list = craw(CARW_NUMBER,'qmRkvKo-KbQ',10)
        raw_list = batch_craw(CARW_NUMBER, # type: ignore
                              {
                                #   不良林
                                  'bulianglin': {
                                      'channel_id': f'{BULIANGLIN_CHANEL_ID}',
                                      'func': bulianglin.bulianglin_func
                                  },
                                #   长风
                                  'changfeng': {
                                     'channel_id':  f'{CHANGFENG_CHANNEL_ID}',
                                     'func': changfeng.changfeng_func
                                  }  
                              }
                            ,CRAW_SLEEP_SECONDS)
        # 有新的订阅才更新
        logging.info(f'==================================================总数据源:{len(raw_list)}个')
        if not len(raw_list)==0:
            # 生成qx专用订阅
            generate_ini = converter.generate_template_ini
            logging.info(f'=========================================================================生成qx配置文件...')
            generate_ini = converter.add_quanx(raw_list,generate_ini)
            logging.info(f'=========================================================================qx配置文件已生成!')
            # 生成clash配置文件
            logging.info(f'=========================================================================生成clash配置文件...')
            generate_ini = converter.add_clash(raw_list,generate_ini)
            logging.info(f'=========================================================================clash配置文件已生成!')

            # 生成v2ray订阅
            logging.info(f'=========================================================================生成v2ray配置文件...')
            generate_ini = converter.add_v2ray(raw_list,generate_ini)
            logging.info(f'=========================================================================v2ray配置文件已生成!')

            # 随机生成一个文件 保持仓库处于活跃
            open('dist/dist-version','w+').write(time.strftime("%Y-%m-%d",time.localtime(time.time()))+'-'+''.join \
                                                 (random.sample('-abcdefghigklmnopqrstuvwxyz1234567890',20)))
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')
            logging.info(f'')
            logging.info(f'=========================================================================节点更新完成!')
    except Exception as e:
        raw_list = []
        logging.info(f'爬取yt频道出错:{e}')