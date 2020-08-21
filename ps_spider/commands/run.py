# -*- encoding: utf-8 -*-
"""
@File    : command.py
@Time    : 2020/8/16 22:19
@Author  : Perry
@Email   : 3500396415@qq.com
@Software: PyCharm
"""
import json
import os

import scrapy
import logging
from scrapy.commands import crawl, ScrapyCommand
from scrapy.exceptions import UsageError
import config

class Run(crawl.Command):

    def add_options(self, parser):
        # 为命令添加选项
        ScrapyCommand.add_options(self, parser)
        # add_option 第一个参数只能是单个字符
        # parser.add_option("-key", "--keyword",  type="str",dest="keyword",action='store', default= json.dumps( config.keyword),
        #                   help="设置爬取分类/关键字")
        parser.add_option("-K", "--keyword",  type="str",dest="keyword",action='store', default= json.dumps( config.keyword),
                          help="设置爬取分类/关键字")
        parser.add_option("-I", "--watermark_img_path", type="str",  dest="watermark_img_path", default=config.watermark_img_path,
                          help="")
        parser.add_option("-T", "--watermark_text", type="str",  dest="watermark_text", default=config.watermark_text,
                          help="")
        parser.add_option("-S", "--timeout", type="int",  dest="timeout", default=config.timeout,
                          help="")
        parser.add_option("-V", "--video_path", type="str", dest="video_path", default=config.VIDEO_SAVE_PATH,
                          help="")
        parser.add_option("-F", "--files_store", type="str", dest="files_store", default=config.FILES_STORE,
                          help="")


    # def parse_default_args(self):
    #     self.settings.set('keywords',config.keyword)
    #     self.settings.set('watermark_img_path',config.watermark_img_path)
    #     self.settings.set('watermark_text',config.watermark_text)
    #     self.settings.set('watermark_text',config.watermark_text)
    #     self.settings['CLOSESPIDER_TIMEOUT'] = config.timeout


    def parse_from_cmdline(self, args, opts):
        keywords  = json.loads(opts.keyword)
        self.settings.set('keywords', keywords, priority='cmdline')
        self.settings.set('watermark_img_path', opts.watermark_img_path, priority='cmdline')
        self.settings.set('watermark_text', opts.watermark_text, priority='cmdline')
        self.settings.set('video_path', opts.video_path, priority='cmdline')

        self.settings['CLOSESPIDER_TIMEOUT'] = opts.timeout
        self.settings['FILES_STORE'] = opts.files_store
        # 设置 JOBDIR
        # -s JOBDIR=crawls/somespider-1
        if not os.path.exists( config.JOBDIR_PATH):
            os.makedirs(config.JOBDIR_PATH)

        dirlist = [int(i) for i in os.listdir(config.JOBDIR_PATH)]
        if dirlist:
            dirlist.sort()
            job_name = dirlist[-1] + 1
        else:
            job_name = 1

        self.settings['JOBDIR'] = f'jobdir/{job_name}'





    def process_options(self, args, opts):
        # 处理从命令行中传入的选项参数
        ScrapyCommand.process_options(self, args, opts)
        # print(self.settings.__dict__)
        # if not os.path.exists(os.path.dirname(self.settings.attributes.get('LOG_FILE').value)):
        #     os.makedirs(os.path.dirname(self.settings.attributes.get('LOG_FILE').value))

        # 加载默认配置
        # self.parse_default_args()
        self.parse_from_cmdline(args,opts)


        # 设置

    def run(self, args, opts):
        self.crawler_process.crawl('pornhub')
        self.crawler_process.start()

