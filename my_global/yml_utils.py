import yaml
'''
    配置文件读取、写入封装
'''

class YamlHandler:

    def __init__(self,file):
        '''
        :param file: yamal文件路径
        '''
        self.file = file

    #   读取yaml数据
    def read_yaml_data(self):
        with open(self.file,encoding='utf-8') as f:
            data = yaml.load(f.read(),Loader=yaml.FullLoader)
        return data

    #写入yaml数据
    def write_yaml_data(self,key, value):
        """

        :param key: 字典的key
        :param value: 写入的值
        :return:
        """
        with open(self.file, 'r', encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        doc[key] = value
        # for item in doc:
        #     item[key] = value
        with open(self.file, 'w', encoding="utf-8") as f:
            yaml.safe_dump(doc, f, default_flow_style=False,allow_unicode=True,sort_keys=False)




if __name__ == '__main__':
    handler = YamlHandler('test.yml')
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
    pass
