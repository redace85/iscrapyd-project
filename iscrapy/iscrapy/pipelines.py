# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdpter
from scrapy.exceptions import DropItem
import sqlite3
import os
import json
import time


import telebot
from telebot import formatting
from itemadapter import ItemAdapter


class ConditionalPipeline:
    '''
    store all conditional into db.
    and use the data to execute judgements
    !!! this pipline should run first!!!
    '''
    def open_spider(self, spider):
        # databases for specific spiders
        if spider.name in ["coin-market"]:
            db_name = f'./{spider.name}.db'

            self.db_data = dict()
            if os.path.isfile(db_name):
                self.con = sqlite3.connect(db_name)
                cur = self.con.cursor()
                for row in cur.execute('SELECT * FROM storage'):
                    self.db_data[row[0]] = row[1]
            else:
                # create table if not exist
                self.con = sqlite3.connect(db_name)
                cur = self.con.cursor()
                cur.execute('CREATE TABLE storage(name TEXT PRIMARY KEY, value ANYTHING)')
            self.data = list()

    def close_spider(self, spider):
        if spider.name in ["coin-market"]:
            # update data
            if self.data and len(self.data) != 0:
                cur = self.con.cursor()
                cur.executemany('INSERT OR REPLACE INTO storage VALUES(?, ?)', self.data)
                self.con.commit()
            self.con.close()

    def process_item(self, item, spider):
        if spider.name == 'coin-market':
            if self.coin_market_process_item(item):
                raise DropItem(f'Drop item')

        return item

    def coin_market_process_item(self, item):
        if item['failed'] is True:
            # parse failed
            return False

        data = item['data']
        if data['symbol'] in self.db_data:
            # conditional branch whether to drop item 
            item_data = json.loads(self.db_data[data['symbol']])

            # price chang percent
            if abs((item_data['price'] - data['price']) / data['price']) < 0.01:
                return True

        # save to db when closed 
        self.data.append((
            data['symbol'], 
            json.dumps({
                'price': data['price'],
                'PC1h': data['percent_change_1h'],
                'PC24h': data['percent_change_24h'],
                'last_updated': data['last_updated'],
                })
            )
                         )
        return False

class TelegramPipeline:
    '''
    this pipline is used for send telegram msg.
    '''
    def __init__(self, tele_token, chat_id, alarm_id):
        self.tele_token = tele_token
        self.chat_id = chat_id
        self.alarm_id = alarm_id
        self.bot = telebot.TeleBot(self.tele_token, threaded=False)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                tele_token=crawler.settings.get('TELE_TOKEN'),
                chat_id=crawler.settings.get('TELE_CHAT_ID'),
                alarm_id=crawler.settings.get('TELE_ALARM_ID'),
                )

    def process_item(self, item, _spider):
        ia = ItemAdapter(item)
        msg = ia['msg']
        msg = formatting.format_text(msg, separator="\n\n")

        # send message to telegram
        if ia['failed'] is False:
            self.bot.send_message(self.chat_id, msg, parse_mode='HTML')
        else:
            self.bot.send_message(self.alarm_id, msg, parse_mode='HTML')

        # sleep 1s after sent
        time.sleep(1)

        return item


