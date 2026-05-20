import scrapy

from iscrapy.items import IscrapyItem 
import time

SECONDS_PER_DAY = 86400

class YahooFinanceSpider(scrapy.Spider):
    name = "yahoo-finance"
    chat_id = "@scrapy_crypto_infos"
    # symbol is pass by arg a
    symbol = 'BTC-USD'
    # GC=F gold
    period1 = 0
    period2 = 0

    def start_requests(self):
        # api_key = self.settings.get('API_KEY')
        # if len(api_key)==0:
        #     raise Exception('No api_key id is given!')

        if 0== self.period2:
            self.period2 = int(time.time())

        if 0== self.period1:
            self.period1 = self.period2 - (5 * SECONDS_PER_DAY)

        # period1 = 867807000 
        # period2 = 1741262400

        self.url =(
         f'https://query1.finance.yahoo.com/v8/finance/chart/{self.symbol}?'
         f'period1={self.period1}&period2={self.period2}&interval=1d&includePrePost=true&events=div%7Csplit%7Cearn'
        )
        headers = {
                'User-Agent' : 'PostmanRuntime/7.36.0',
                'Accept-Encoding' : 'gzip, deflate, br'
                }
        yield scrapy.http.JsonRequest(url=self.url, dont_filter=True, headers=headers, callback=self.parse)

    def parse(self, response):
        if response.status != 200:
            raise Exception(f'query failed with code {response.status}')
        
        res = response.json()

        try:

            chart_result = res['chart']['result'][0]
            timestamp = chart_result['timestamp']
            quote = chart_result['indicators']['quote'][0]
            for i in range(len(timestamp)):
                data = {} 
                data['timestamp'] = timestamp[i]

                data['open'] = quote['open'][i]
                data['high'] = quote['high'][i]
                data['low'] = quote['low'][i]
                data['close'] = quote['close'][i]
                data['volume'] = quote['volume'][i]

                item = IscrapyItem(msg='', failed=False, data=data, item_id=timestamp[i])
                yield item
        except Exception as e:
            msg = f'spider: {self.name} url: {self.url} error: {e}'
            item = IscrapyItem(msg=msg, failed=True)
            yield item

