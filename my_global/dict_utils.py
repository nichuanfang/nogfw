from collections import OrderedDict

def modify_dict(source_dict, new_key, old_key, value):
    """
    处理字典source_dict 在old_key之前插入new_key:value键值对 返回一个新的字典
    """
    new_dict = OrderedDict()
    for k, v in source_dict.items():
        if k == old_key:
            new_dict[new_key] = value
        new_dict[k] = v
    return dict(new_dict)