import logging
import cv2
import sys
import io
from PIL import Image
import colorlog
 
# 通过此flag 开启本地开发模式
try:
    # 如果有环境变量 说明是测试/生产环境
    NEED_SAVE = sys.argv[3]
    local = False
except:
    # 如果没有环境变量 启动本地环境
    local = True
 
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
 '%(log_color)s%(levelname)s:%(name)s:%(message)s'))

# 带颜色的logger 
logging = colorlog.getLogger()
logging.addHandler(handler)

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