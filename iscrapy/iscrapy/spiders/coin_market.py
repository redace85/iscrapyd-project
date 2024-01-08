import scrapy
from scrapy.linkextractors import LinkExtractor


class CoinMarketSpider(scrapy.Spider):
    name = "coin-market"
    allowed_domains = ["pro-api.coinmarketcap.com"]
    crypto_ids = list()

    def start_requests(self):
        self.crypto_ids = self.settings.getlist('CRYPTO_IDS')
        if len(self.crypto_ids)==0:
            raise Exception('No crypto id is given!')
        
        api_key = self.settings.get('API_KEY')
        if len(api_key)==0:
            raise Exception('No api_key id is given!')

        ids_string = ','.join(self.crypto_ids)
        url = f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id={ids_string}&aux=total_supply'
        headers = {
                'X-Cmc_Pro_Api_Key' : api_key,
                'User-Agent' : 'PostmanRuntime/7.36.0',
                'Accept-Encoding' : 'gzip, deflate, br'
                }
        yield scrapy.http.JsonRequest(url=url, dont_filter=True, headers=headers, callback=self.parse)

    def parse(self, response):
        if response.status != 200:
            raise Exception(f'query failed with code {response.status}')
        
        res = response.json()

        # fetch data unit by id
        for i in self.crypto_ids:
            unit = res['data'][i]

            # returned item
            item = {}
            item['symbol'] = unit['symbol']
            item['last_updated'] = unit['last_updated']

            quote_usd = unit['quote']['USD']
            item['price'] = quote_usd['price']
            item['percent_change_1h'] = quote_usd['percent_change_1h']
            item['percent_change_24h'] = quote_usd['percent_change_24h']

            yield item

