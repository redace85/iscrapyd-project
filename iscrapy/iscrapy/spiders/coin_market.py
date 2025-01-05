import scrapy

from iscrapy.items import IscrapyItem 


class CoinMarketSpider(scrapy.Spider):
    name = "coin-market"
    allowed_domains = ["pro-api.coinmarketcap.com"]

    def start_requests(self):
        self.crypto_ids = self.settings.getlist('CRYPTO_IDS')
        if len(self.crypto_ids)==0:
            raise Exception('No crypto id is given!')
        
        api_key = self.settings.get('API_KEY')
        if len(api_key)==0:
            raise Exception('No api_key id is given!')

        ids_string = ','.join(self.crypto_ids)
        self.url = f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id={ids_string}&aux=total_supply'
        headers = {
                'X-Cmc_Pro_Api_Key' : api_key,
                'User-Agent' : 'PostmanRuntime/7.36.0',
                'Accept-Encoding' : 'gzip, deflate, br'
                }
        yield scrapy.http.JsonRequest(url=self.url, dont_filter=True, headers=headers, callback=self.parse)

    def parse(self, response):
        if response.status != 200:
            raise Exception(f'query failed with code {response.status}')
        
        res = response.json()

        try:
            # fetch data unit by id
            for i in self.crypto_ids:
                unit = res['data'][i]
                data = {} 
                data['symbol'] = unit['symbol']
                data['last_updated'] = unit['last_updated']

                quote_usd = unit['quote']['USD']
                data['price'] = quote_usd['price']
                data['percent_change_1h'] = quote_usd['percent_change_1h'],
                data['percent_change_24h'] = quote_usd['percent_change_24h'],

                # assemble msg to send
                msg = '{}\nprice: {}\nPC1h: {}\nPC24h: {}\nUpdated: {}'.format(
                        data['symbol'],
                        data['price'],
                        data['percent_change_1h'],
                        data['percent_change_24h'],
                        data['last_updated']
                        )
                item = IscrapyItem(msg=msg, failed=False, data=data)
                yield item
        except:
            # parse failed; notify developer
            msg = f'spider: {self.name} url: {self.url}'
            item = IscrapyItem(msg=msg, failed=True)
            yield item

