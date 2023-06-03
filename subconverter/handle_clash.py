# 定制化生成的clash配置文件 
#!/usr/local/bin/python
# coding=utf-8
import sys
import io
from my_global.yml_utils import YamlHandler

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')


def format():
    handler = YamlHandler(f'dist/clash-sub.txt')
    data = handler.read_yaml_data()
    proxy_groups = data['proxy-groups']
    for group in proxy_groups:
        if group['name'] == '♻️ 低延迟':
            group['lazy'] = True
        elif group['name'] == '🤔 高可用':
            group['lazy'] = True
        elif group['name'] == '🇭🇰 Hong Kong':
            group['lazy'] = True
        elif group['name'] == '🇸🇬 Singapore':
            group['lazy'] = True
        elif group['name'] == '🇹🇼 Taiwan':
            group['lazy'] = True
        elif group['name'] == '🇺🇸 United States':
            group['lazy'] = True
        elif group['name'] == '🇯🇵 Japan':
            group['lazy'] = True
        elif group['name'] == '🇰🇷 Korea':
            group['lazy'] = True
        else:
            pass
    handler.write_yaml_data('proxy-groups',proxy_groups)




