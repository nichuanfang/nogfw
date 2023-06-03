# 图片识别OCR模块
import easyocr
from  easyocr import Reader

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


