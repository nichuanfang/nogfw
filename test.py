#!/usr/local/bin/python
# coding=utf-8
from my_global import ocr_utils
# 测试模块
if __name__ == '__main__':

    res = ocr_utils.read_text('dist/local/changfeng.jpg',ocr_utils.get_reader())
    
    password = ocr_utils.get_changfeng_password(res) # type: ignore
    pass

