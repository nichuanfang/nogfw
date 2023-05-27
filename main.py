# 整合全网的vps 发布私人订阅

import requests
from urllib import request, parse
from requests import Request
from requests import Response
import json
import re
import base64
import telnetlib
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

def check_proxy(ip, port):
    try:
        telnetlib.Telnet(ip, port, timeout=3)
        logging.info(f"代理IP:{ip}:{port}有效！")
        return True
    except:
        logging.warn(f"代理IP:{ip}:{port}无效！")
        return False

with open('source.txt','r') as source_file:
    lines = source_file.readlines()

all_nodes = []
test_latency_list = []

for line in lines:
    if line.startswith('(base64)'):
        res = requests.get(line[8:].replace('\'','').replace('\"','').replace('\n',''))
        # 对结果base64解码
        nodes = str(base64.b64decode(res.text),encoding='utf-8').split('\n')
    else:
        res = requests.get(line.replace('\'','').replace('\"','').replace('\n',''))
        nodes = res.text.split('\n')
    if len(nodes) != 0 :
        final_nodes = []
        for node_item in nodes:
            if node_item.lstrip().startswith('vmess'):
                node_str = str(base64.b64decode(node_item.split('//')[1]), encoding = "utf-8")
                node_json = json.loads(node_str)
                # 匹配vmess密码的正则 如果存在vmess协议密码不是形如b65da4af-a12a-4a59-9316-4549e12ba62c的直接舍弃
                if re.match(r'^(\d|\w){8}-(\d|\w){4}-(\d|\w){4}-(\d|\w){4}-(\d|\w){12}$',node_json['id']):
                    final_nodes.append(node_item)
            else:
                # 其他协议规则以后再加
                final_nodes.append(node_item)
        all_nodes+=final_nodes
# 去重
all_nodes = list(set(all_nodes))
# 去空串
all_nodes = [x for x in all_nodes if x != '']

# 测试支持一定订阅转换最多多少个
# test_params = '|'.join(all_nodes[:15])
# sub_res = requests.get(f'https://sub.xeton.dev/sub?target=quanx&url={parse.quote(test_params)}&insert=false')

# 步长15
for item in [all_nodes[i:i+15] for i in range(0,len(all_nodes),15)]:
    sub_res = requests.get(f'https://sub.xeton.dev/sub?target=quanx&url={parse.quote("|".join(item))}&insert=false')
    sub_res_list = sub_res.text.split('\n')
    for index,subitem in enumerate(sub_res_list):
        if subitem == '[server_local]' and sub_res_list[index+1].startswith(('shadowsocks ','vmess','trojan','socks5','http')):
            # 添加到目标节点中
            test_latency_list+=sub_res_list[index+1:index+len(item)+1]

# open('raw_servers.list','w+',encoding='utf8').write('\n'.join(all_nodes))
# open('test_latency_servers.list','w+',encoding='utf8').write('\n'.join(test_latency_list))

final_servers = []
# 测试延迟 过滤出最佳vps 生成dist
for test_node in test_latency_list:
    try: 
        if check_proxy(test_node.split(',')[0].split(' = ')[1].split(':')[0],test_node.split(',')[0].split(' = ')[1].split(':')[1]):
            # 继续进行检测 方法: https://developer.aliyun.com/article/1147404
            final_servers.append(test_node)
    except:
        continue

open('servers.list','w+',encoding='utf8').write('\n'.join(final_servers))
