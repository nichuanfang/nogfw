import logging
import cv2
import easyocr
import sys
import io
from collections import OrderedDict
import yaml
import copy
import re
from PIL import Image

# 通过此flag 开启本地开发模式
local = False

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
# 日志配置
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# 图像识别器  windows下需要先下载模型文件  https://blog.csdn.net/Loliykon/article/details/114334699
reader = easyocr.Reader(['ch_sim', 'en'], model_storage_directory='ocr_models')

# 二维码识别
def qr_recognize(file_path: str):
    qrcode_filename = file_path
    qrcode_image = cv2.imread(qrcode_filename)
    qrCodeDetector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = qrCodeDetector.detectAndDecode(qrcode_image)
    return data

def resize(file):
    """图片重新分配大小

    Args:
        file (_type_): 图片
    """    
    im = Image.open(file)
    reim=im.resize((640, 640))#宽*高

    reim.save(file,dpi=(300.0,300.0)) ##200.0,200.0分别为想要设定的dpi值

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