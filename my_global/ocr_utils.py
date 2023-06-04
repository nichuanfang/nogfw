# 图片识别OCR模块
from distutils.command import sdist
import random
import easyocr
from  easyocr import Reader
import re

# 获取读取器
def get_reader(lang_list:list[str]=['en']):
    # 图像识别器  windows下需要先下载模型文件  https://blog.csdn.net/Loliykon/article/details/114334699
    # ['ch_sim', 'en']
    return easyocr.Reader(lang_list, model_storage_directory='ocr_models')

# 读取图片获取简单结果
def read_text(image:str,reader:Reader):
    return reader.readtext(image,detail = 0)

# 获取图片获取详细结果
def read_detail_text(image:str,reader:Reader):
    return reader.readtext(image,detail = 1)

# 获取长风频道的密码
def get_changfeng_password(ocr_result:list[str]):
    secret = ''
    for index,item in enumerate(ocr_result):
        if index>8 and (item.__contains__('V2rayse') or item.__contains__('VZrayse') or item.__contains__('comlfree') or item.__contains__('free-node')) and len(item)>=19: # type: ignore
            # 在剩下的元素中寻找密码
            remaining_index = index
            while True:
                if remaining_index == len(ocr_result):
                    break
                # 向下读取 正则匹配 4-6位 (a-z) 
                remaining_index = remaining_index+1
                if bool(re.search(r'^[a-z]{3,6}$',ocr_result[remaining_index])):
                    # lower()防止OCR识别成了大写
                    secret = ocr_result[remaining_index].lower()
                    # 符合条件就返回
                    break
                
            if secret != '':
                break
            else:
                raise RuntimeError('changfeng password ocr parsed error!')
    return secret
    
               