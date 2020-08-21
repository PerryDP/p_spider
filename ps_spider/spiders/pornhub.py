import datetime
import hashlib
import logging
import os
import re
from urllib import parse
import traceback

import execjs
import js2py
import requests
import scrapy

from ps_spider.items import PsSpiderItem, PsVideoItem


class PornhubSpider(scrapy.Spider):
    name = 'pornhub'
    allowed_domains = []
    # start_urls = ['http://cn.pornhub.com/video/search?search=%E5%9B%BD%E4%BA%A7']
    start_urls = []
    fenlei = {}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # 重写此方法使得可以在init中直接获取settings
        spider = super(PornhubSpider, cls).from_crawler(crawler, crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def __init__(self, *args, **kwargs):
        super(PornhubSpider, self).__init__()
        for fenlei, keys in args[0]['keywords'].items():
            for key in keys:
                PornhubSpider.fenlei[key] = fenlei
                quote_key = parse.quote(key)
                PornhubSpider.start_urls.append(
                    f'https://cn.pornhub.com/video/search?search={quote_key}'
                )

    def validateName(self,name):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_name = re.sub(rstr, "_", name)  # 替换为下划线
        return new_name
    def get_item(self, response):
        info = {
            'name': response.meta['name'],
            'md5_name': response.meta['md5_name'],
            'file_type': response.meta['file_type'],
            'fenlei': response.meta['fenlei'],
            'content': response.body,
        }
        info['path'] = os.path.join(self.settings['video_path'], info['fenlei'], info['md5_name'],
                                    f"{info['md5_name']}.{info['file_type']}")
        logging.info(f'download {info["name"]}.{info["file_type"]} ,timeout {response.meta["download_timeout"]}')
        item = PsSpiderItem(info)
        return item
    def get_video_item(self,response):
        info = {
            'name': response.meta['name'],
            'md5_name': response.meta['md5_name'],
            'file_type': response.meta['file_type'],
            'fenlei': response.meta['fenlei'],
            'label':response.meta['label'],
            'px':response.meta['px'],
            'watermark_img_path':self.settings['watermark_img_path']
        }
        item = PsVideoItem(info)
        return item

    def save_jpg_error(self, response):
        print('失败', response.meta)
        print('失败', response.body)

    def parse_detail(self, items, response, *args, **kwargs):
        '''
        解析列表页，首先保存webm
        :param items:
        :param response:
        :param args:
        :param kwargs:
        :return:
        '''
        reqs = {'jpg': [], 'webm': []}
        for i in items:
            try:
                v_key = i.xpath('@href')[0].extract()
                v_key = v_key.split('=ph')[-1]
                v_title = i.xpath('@title')[0].extract()
                print(f'key={v_key},title ={v_title}')
                fenlei = self.fenlei[parse.unquote(response.url.split('search=')[-1])]
                print(fenlei)
                md5_title = hashlib.md5(v_title.encode('utf-8')).hexdigest()
                print('md5title=', md5_title)
                v_jpg_url = i.xpath('img/@data-src')[0].extract()
                print('v_jpg_url=', v_jpg_url)
                # jpg图片
                jpg_requests = scrapy.Request(v_jpg_url, callback=self.get_item, errback=self.save_jpg_error)
                jpg_requests.meta['fenlei'] = fenlei
                jpg_requests.meta['name'] = v_title
                jpg_requests.meta['md5_name'] = md5_title
                jpg_requests.meta['file_type'] = v_jpg_url.split('.')[-1]
                reqs['jpg'].append(jpg_requests)
                # webm
                webm_url = i.xpath('img/@data-mediabook')[0].extract()
                webm_requests = scrapy.Request(webm_url, callback=self.get_item)
                webm_requests.meta['fenlei'] = fenlei
                webm_requests.meta['name'] = v_title
                webm_requests.meta['md5_name'] = md5_title
                webm_requests.meta['file_type'] = 'webm'
                reqs['webm'].append(webm_requests)
            except Exception as e:
                pass
        return reqs


    def video_detail_page(self, response):
        # with open(f'html/{response.meta["name"]}.html', 'wb') as f:
        #     f.write(response.body)
        js_temp = response.xpath('//script/text()').extract()
        for i in js_temp:
            if "flashvars" in i:
                js = i
                flashvars = re.findall("flashvars_\d+", js)[0]
                js = "".join(js.split("\n\t")[:-5]).strip()
                js_result = js2py.eval_js(js + flashvars)

                # video_url = js_result.quality_1080p or js_result.quality_720p or js_result.quality_480p or js_result.quality_240p or ''
                video_url = px = ''
                if js_result.quality_1080p:
                    video_url = js_result.quality_1080p
                    px = '1080'
                elif js_result.quality_720p:
                    video_url = js_result.quality_720p
                    px = '720'
                elif js_result.quality_480p:
                    video_url = js_result.quality_480p
                    px = '480'
                elif js_result.quality_240p:
                    video_url = js_result.quality_240p
                    px = '240'

                if video_url:
                    labels = response.xpath('//div[@class="categoriesWrapper"]/a/text()').extract()
                    labels = ','.join(labels)
                    info = {
                        'name': response.meta['name'],
                        'md5_name': response.meta['md5_name'],
                        'file_type': video_url.split('?')[0].split('.')[-1],
                        'fenlei': response.meta['fenlei'],
                        'file_urls' : video_url,
                        'label': labels,
                        'px':px,
                        'watermark_img_path':self.settings['watermark_img_path']
                    }
                    info['path'] = os.path.join(self.settings['video_path'], info['fenlei'], info['md5_name'],
                                    f"{info['md5_name']}.{info['file_type']}")
                    video_item = PsVideoItem(info)

                    return video_item

    def check_exist(self,md5_name):
        '''
        同步接口请求文件是否已经存在
        :return:
        '''

        return False

    def parse(self, response):

        # with open(f'html/{parse.unquote(response.url.split("search=")[-1])}.html' ,'wb') as f:
        #     f.write(response.body)

        need_go = response.xpath('//body[@onload="go()"]')
        if need_go:
            print('需要跳转')
            self.get_go(response)
            return
        page_item = response.xpath('//*[@class="phimage"]/a')

        for i in page_item:
            try:
                v_key = i.xpath('@href')[0].extract()
                v_key = v_key.split('=ph')[-1].strip()
                v_title = self.validateName(i.xpath('@title')[0].extract())

                fenlei = self.fenlei[parse.unquote(response.url.split('search=')[-1])]

                md5_title = hashlib.md5(v_title.encode('utf-8')).hexdigest()

                # 查看是否存在
                if self.check_exist(md5_title):
                    continue


                v_jpg_url = i.xpath('img/@data-src')[0].extract()
                meta = {
                    'fenlei': fenlei,
                    'name': v_title,
                    'md5_name': md5_title
                }
                # jpg图片
                jpg_requests = scrapy.Request(v_jpg_url, callback=self.get_item, errback=self.save_jpg_error)
                jpg_requests.meta.update(meta)
                jpg_requests.meta['file_type'] = v_jpg_url.split('.')[-1]
                yield  jpg_requests
                # webm
                webm_url = i.xpath('img/@data-mediabook')[0].extract()
                webm_requests = scrapy.Request(webm_url, callback=self.get_item)
                webm_requests.meta.update(meta)
                webm_requests.meta['file_type'] = 'webm'
                yield webm_requests
                # 视频
                video_url = f'https://cn.pornhub.com/view_video.php?viewkey=ph{v_key}'
                video_requests = scrapy.Request(video_url, callback=self.video_detail_page)
                video_requests.meta.update(meta)
                yield video_requests

            except Exception as e:
                traceback.print_exc()

        next_page = response.xpath('//div[@class="page_next omega"]/a/@href')
        if next_page:
            print('下一页',next_page[0])
            yield scrapy.Request(next_page[0],callback=self.parse)

    def get_go(self, response):
        '''
        执行js以获取cookie
        :return:
        '''
        # 获取js代码
        js_ = response.xpath('//script')[0].extract()
        print('js 代码', js_)
        now  = datetime.datetime.now().strftime('%Y%m%d_%H%M%D')
        if not os.path.exists('go'):
            os.makedirs('go')

        with open(f'go/{now}.txt','w',encoding='utf-8') as f:
            f.write(js_)
