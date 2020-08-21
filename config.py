# -*- encoding: utf-8 -*-
"""
@file    : config.py
@time    : 2020/8/16 23:23
@author  : perry
@email   : 3500396415@qq.com
@software: pycharm
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
JOBDIR_PATH = os.path.join(BASE_DIR, 'jobdir')

VIDEO_SAVE_PATH = os.path.join(BASE_DIR,'video')
FILES_STORE = VIDEO_SAVE_PATH

watermark_img_path = r"d:\头像资源\02021.jpg"    # 水印地址，绝对路径
watermark_text = r"3500396415"     # 水印文字，有地址时不生效


# closespider_timeout = 0  一个整数值，单位为秒
# closespider_pagecount = 0
# closespider_itemcount = 0
# closespider_errorcount = 0
timeout = 4 * 60 * 60      # 规定的运行时长 当前4小时



# 搜索字符串
keyword = {
    "guochan":['国产','台湾','swag','麻豆','91'],
    "oumei":['american','model','hot','beautiful','teen'],
    "rihan":['日本','japanese','韩国','korea','jav'],
    "zhubo":['主播'],
    "dongman":['3d','2d','anime','hentai'],
    "shuangfei":['双飞','one guy'],

}

if __name__ == '__main__':
    print(BASE_DIR)