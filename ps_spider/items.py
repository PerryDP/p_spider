# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PsSpiderItem(scrapy.Item):
    name = scrapy.Field()
    md5_name = scrapy.Field()
    path = scrapy.Field()
    fenlei = scrapy.Field()
    content = scrapy.Field()
    file_type = scrapy.Field()


class PsVideoItem(scrapy.Item):
    name = scrapy.Field()
    md5_name = scrapy.Field()
    fenlei = scrapy.Field()
    file_type = scrapy.Field()
    px = scrapy.Field()
    watermark_img_path = scrapy.Field()
    # 文件item 使用path会在下载后覆盖成本地路径
    path = scrapy.Field()
    label = scrapy.Field()

    file_urls = scrapy.Field()
    files = scrapy.Field()