# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IscrapyItem(scrapy.Item):
   # item_id string to send
   item_id = scrapy.Field()
   # data to store info
   data = scrapy.Field()
   # whether failed
   failed = scrapy.Field()
   # msg string to send
   msg = scrapy.Field()
   pass
