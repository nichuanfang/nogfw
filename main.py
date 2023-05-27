# 整合全网的vps 发布私人订阅

import requests
from urllib import request, parse
from requests import Request
from requests import Response

with open('source.txt','r') as source_file:
    lines = source_file.readlines()

all_nodes = []
test_latency_list = []

for line in lines:
    res = requests.get(line.replace('\'','').replace('\"','').replace('\n',''))
    nodes = res.text.split('\n')
    if len(nodes) != 0 :
        all_nodes+=nodes
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

open('servers.list','w+',encoding='utf8').write('\n'.join(test_latency_list))
pass

