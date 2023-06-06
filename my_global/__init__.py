# import logging
from loguru import logger as logging 
# from tqdm import tqdm 进度条
import cv2
import sys
import io
from PIL import Image
 
# 通过此flag 开启本地开发模式
local = True if len(sys.argv)==1 else False

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
# 日志配置
# LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

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