#!/usr/local/bin/python
# coding=utf-8
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')


# 生成qx的节点订阅
with open(f'dist/quanx-sub.txt','r+',encoding='utf-8') as quanx_f:
    quanxs = quanx_f.readlines()


final_quanx = []
for quanx in quanxs:
    if quanx =='[server_local]\n':
        continue
    elif quanx == '\n':
        continue
    if quanx.startswith(('vmess','trojan','shadowsocks','http','socks')):
         final_quanx.append(quanx)
    else:
        break

with open(f'dist/quanx-sub.txt','w+',encoding='utf-8') as quanx_wf:
            quanx_wf.writelines(final_quanx)
