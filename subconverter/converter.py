# 处理generate.ini文件
import re
from urllib import request, parse
import requests,base64,json,urllib
from urllib import parse
import json
import base64
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# quanx的正则
quanx_pattern = r'{quanx}'
# clash的正则
clash_pattern = r'{clash}'
# v2ray的正则
v2ray_pattern = r'{v2ray}'

def decode_base64(data, decode_utf8=True):
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '='* missing_padding
    if decode_utf8:
        return base64.urlsafe_b64decode(data.encode('ascii')).decode("utf-8")
    else:
        return base64.urlsafe_b64decode(data.encode('ascii'))

def encode_base64(data):
    return base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8")

def get_remarks(ssrConfig):
    param = parse.parse_qs(parse.urlsplit(ssrConfig).query)
    remarks_base64 =  param['remarks'][0].replace('-', '+').replace('_', '/')
    remarks = decode_base64(remarks_base64, False)
    return parse.quote(remarks)

def convert_ssr2ss(ssrConfig):
    ssConfig = "ss://"
    networkConfig = ssrConfig.split('/?')[0].split(':')
    serverIP = networkConfig[0]
    serverPort = networkConfig[1]
    encryption = networkConfig[3]
    passwd = decode_base64(networkConfig[5])
    remarks = get_remarks(ssrConfig)
    ssConfig += encode_base64(encryption + ":" + passwd) + "@" + serverIP + ":" + serverPort + "/#" + remarks
    return ssConfig

def sort_func(proxy):
        # 获取测速结果
        match = re.search(r'\d+.\d+',proxy.split('-')[-1])
        if match is not None:
            if proxy.split('-')[-1].lower().__contains__('mb'):
                return float(match.group())*1000
            return float(match.group())
        return 0.0

def get_tag(node:str):
    type = node.split('://')[0]
    # 获取节点的原始标签
    # ss
    if type == 'ss':
        logging.info(f'开始处理ss节点:{node}')
        urlencoded_node = node.split('#')[1]
        # url解码
        return parse.unquote(urlencoded_node)
    if type == 'ssr':
        logging.info(f'开始处理ssr节点:{node}')
        b64encoded_node = node.split('//')[1]
        sconfig = decode_base64(b64encoded_node)
        # ss链接
        ss_node = convert_ssr2ss(sconfig)
        return (parse.unquote(ss_node.split('#')[1]),ss_node)
    # trojan
    elif type == 'trojan':
        logging.info(f'开始处理trojan节点:{node}')
        urlencoded_node = node.split('#')[1]
        return parse.unquote(urlencoded_node)
    # vmess
    elif type == 'vmess':
        logging.info(f'开始处理vmess节点:{node}')
        # 先对vmess协议后面base64解码 转为json 其中的ps字段即为tag
        b64encoded_node = node.split('//')[1]
        b64decoded_node = base64.b64decode(b64encoded_node).decode('utf-8')
        json_node = json.loads(b64decoded_node)
        return json_node['ps']
    else:
        logging.info(f'未知协议节点:{node}')
        return 'none'

def tag(node:str,new_tag):
    type = node.split('://')[0]
    # 给节点替换新的tag
     # ss
    if type == 'ss':
        logging.info(f'开始给ss节点:{node}打tag')
        urlencoded_node = node.split('#')[1]
        # url解码
        return node.split('#')[0]+'#'+ parse.quote(new_tag)
    if type == 'ssr':
        logging.info(f'开始给ssr节点:{node}打tag')
        b64encoded_node = node.split('//')[1]
        sconfig = decode_base64(b64encoded_node)
        # ss链接
        urlencoded_node = convert_ssr2ss(sconfig).split('#')[1]
        return parse.unquote(urlencoded_node)
    # trojan
    elif type == 'trojan':
        logging.info(f'开始给trojan节点:{node}打tag')
        urlencoded_node = node.split('#')[1]
        return node.split('#')[0]+'#'+ parse.quote(new_tag)
    # vmess
    elif type == 'vmess':
        logging.info(f'开始给vmess节点:{node}打tag')
        # 先对vmess协议后面base64解码 转为json 其中的ps字段即为tag
        b64encoded_node = node.split('//')[1]
        b64decoded_node = base64.b64decode(b64encoded_node).decode('utf-8')
        json_node = json.loads(b64decoded_node)
        json_node['ps'] = new_tag

        json_str = json.dumps(json_node,ensure_ascii=False)
        return 'vmess://'+ base64.b64encode(json_str.encode("utf-8")).decode('utf-8')
    else:
        return node

def handle_nodes(nodes:list[str]):
    # 获取节点tag与该节点的印射字典

    # key: 节点中文名 value: 节点原始数据
    tag_node_dict:dict[str,str] = {}

    for node in nodes:
        get_tag_res = get_tag(node)
        if type(get_tag_res) == tuple:
            tag_node_dict[get_tag_res[0]] = get_tag_res[1] # type: ignore
        else:
            tag_node_dict[get_tag(node)] = node # type: ignore

    sorted_tag_node_keys = sorted(tag_node_dict,key=sort_func,reverse=True)
    new_nodes = []
    # 节点重排序
    for index,sorted_tag_node_key in enumerate(sorted_tag_node_keys):
        sorted_tag_node = tag_node_dict[sorted_tag_node_key]
        # 处理节点 去除特殊标识(例如: youtube不良林) 添加标签 [序号]
        new_nodes.append(tag(sorted_tag_node,f'[{index+1}] '+sorted_tag_node_key.replace('(Youtube:不良林)','')))

    return new_nodes

with open('subconverter/generate_template.ini','r+',encoding='utf-8') as generate_template:
    generate_template_ini = generate_template.read()

def add_quanx(nodes:list[str],template:str = generate_template_ini):
    """添加qx节点

    Args:
        nodes (list[str]): 节点
    """   
    url = '|'.join(handle_nodes(nodes))
    generate_ini = re.sub(quanx_pattern,f'{url}',template)
    with open('subconverter/generate.ini','w+',encoding='utf-8') as f:
        f.write(generate_ini)
    return generate_ini
        

def add_clash(nodes:list[str],template:str = generate_template_ini):
    """添加clash节点

    Args:
        nodes (list[str]): 节点
    """    
    url = '|'.join(handle_nodes(nodes))
    generate_ini = re.sub(clash_pattern,f'{url}',template)
    with open('subconverter/generate.ini','w+',encoding='utf-8') as f:
        f.write(generate_ini)
    return generate_ini

def add_v2ray(nodes:list[str],template:str = generate_template_ini):
    """添加v2ray节点

    Args:
        nodes (list[str]): 节点
    """    
    url = '|'.join(handle_nodes(nodes))
    generate_ini = re.sub(v2ray_pattern,f'{url}',template)
    with open('subconverter/generate.ini','w+',encoding='utf-8') as f:
        f.write(generate_ini)
    return generate_ini
