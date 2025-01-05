# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IscrapyItem(scrapy.Item):
   # data to store info
   data = scrapy.Field()
   # whether failed
   failed = scrapy.Field()
   # msg string to send
   msg = scrapy.Field()
   pass
