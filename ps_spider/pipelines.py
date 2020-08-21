# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import os
import scrapy
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline

from itemadapter import ItemAdapter
import moviepy.editor as mp

class PsSpiderPipeline:
    def process_item(self, item, spider):
        if item.get('file_urls'):
            return item
        if not os.path.exists(os.path.dirname(item['path'])):
            os.makedirs(os.path.dirname(item['path']))
        if item["content"]:
            with open(item['path'], 'wb') as f:
                f.write(item['content'])
            logging.info(f'save {item["name"]}.{item["file_type"]} done')
            return item
        else:
            logging.error(f'save {item["name"]}.{item["file_type"]} 图片下载失败,路径{item["path"]}')
            raise DropItem("download fail")



class PsVideoPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        if not item.get('file_urls'):
            return item
        logging.info(f'start download video: {item["name"]}')
        yield Request(item['file_urls'],
                      meta={
                          'name': item['name'],
                          'file_type': item['file_type'],
                          'fenlei': item['fenlei'],
                          'md5_name': item['md5_name'],
                          'path':item['path'],
                          'px':item['px']
                      })

    def file_path(self, request, response=None, info=None):  # 修改文件路径和文件名
        # file_name = f'{request.meta["fenlei"]}/{request.meta["md5_name"]}/{request.meta["md5_name"]}.{request.meta["file_type"]}'
        # print('文件路径',request.meta['path'])
        return request.meta['path']
    def set_water(self,item):
        try:
            logging.info(f"文件:{item['name']} 开始添加水印")
            video = mp.VideoFileClip(item["path"])
            logo = (mp.ImageClip(item["watermark_img_path"])
                    .set_duration(video.duration)  # 水印持续时间
                    .resize(height=50)  # 水印的高度，会等比缩放
                    .margin(right=10, top=10, opacity=0)  # 水印边距和透明度
                    .set_pos(("right", "top")))  # 水印的位置

            final = mp.CompositeVideoClip([video, logo])
            # 删除原文件
            # os.remove(item["path"])
            # mp4文件默认用libx264编码， 比特率单位bps
            final.write_videofile(item["path"], codec="libx264", bitrate="10000000")
            logging.info(f"文件:{item['name']} 添加水印成功 ,文件路径:{item['path']}")
        except Exception as e:
            logging.error(f"文件:{item['name']} 添加水印失败 ,文件路径:{item['path']}")

    def item_completed(self, results, item, info):
        if not item.get('file_urls'):
            return item
        # result [(True, {'url': 'https://ev.phncdn.com/videos/201911/23/263708462/1080P_4000K_263708462.mp4?validfrom=1597689751&validto=1597696951&rate=50000k&burst=50000k&hash=VW2qzP0Sg%2Br%2Bls0hhpbzLqYFtGQ%3D'
        # , 'path': 'guochan/d5dbce785b71838dbd865b330a1dfd15/d5dbce785b71838dbd865b330a1dfd15.mp4', 'checksum': 'e1f5957aaffe7b125357d6bafcc26eea', 'status': 'downloaded'})]



        if  results[0][0]:
            with open(os.path.join(os.path.dirname(item['path']),item['name'] + '.txt') ,'w',encoding='utf-8') as f :
                f.write(f'名称:{item["name"]}\n')
                f.write(f'类型:{item["file_type"]}\n')
                f.write(f'分类:{item["fenlei"]}\n')
                f.write(f'标签:{item["label"]}\n')
                f.write(f'px:{item["px"]}p\n')
                f.write(f'md5名称:{item["md5_name"]}\n')
                f.write(f'文件路径:{item["path"]}\n')
                f.write(f'源地址:{results[0][1]["url"]}\n')

            logging.info(f'download {item["name"]}.{item["file_type"]} success')
            # 添加水印
            # self.set_water(item)


        else:
            logging.info(f'download  {item["name"]}.{item["file_type"]} fail')
            raise DropItem("download fail")
        with open('已下载视频.txt','a+',encoding='utf-8') as f:
            f.write(f'{list(item.items())}\n')

        return item