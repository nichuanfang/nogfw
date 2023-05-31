# 处理generate.ini文件
import re

# quanx的正则
quanx_pattern = r'{quanx}'
# clash的正则
clash_pattern = r'{clash}'
# mixed的正则
mixed_pattern = r'{mixed}'


with open('subconverter/generate_template.ini','r+',encoding='utf-8') as generate_template:
    generate_template_ini = generate_template.read()

def add_quanx(nodes:list[str]):
    """添加qx节点

    Args:
        nodes (list[str]): 节点
    """   
    url = '|'.join(nodes)
    generate_ini = re.sub(quanx_pattern,f'{url}',generate_template_ini)
    open('subconverter/generate.ini','w+',encoding='utf-8').write(generate_ini)

def add_clash(nodes:list[str]):
    """添加clash节点

    Args:
        nodes (list[str]): 节点
    """    
    url = '|'.join(nodes)
    generate_ini = re.sub(clash_pattern,f'{url}',generate_template_ini)
    open('subconverter/generate.ini','w+',encoding='utf-8').write(generate_ini)

def add_mixed(nodes:list[str]):
    """添加mixed节点 小火箭可用 base64加密

    Args:
        nodes (list[str]): 节点
    """    
    url = '|'.join(nodes)
    generate_ini = re.sub(mixed_pattern,f'{url}',generate_template_ini)
    open('subconverter/generate.ini','w+',encoding='utf-8').write(generate_ini)
