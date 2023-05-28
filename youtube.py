#!/usr/local/bin/python
# coding=utf-8
from time import sleep
import requests
import logging
import io
import sys
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

logging.basicConfig(level=logging.INFO)

# 隔一段时间获取二维码
# ffmpeg -i "$(yt-dlp -g qmRkvKo-KbQ | head -n 1)" -vframes 1 dist/last.jpg

for index in range(2):
    subprocess.call(f'ffmpeg -i "$(yt-dlp -g qmRkvKo-KbQ | head -n 1)" -vframes 1 dist/last_{index}.jpg',shell=True)
    # 处理生成的二维码 生成节点信息
    sleep(30)