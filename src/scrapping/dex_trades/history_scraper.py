import logging
import random
import re
from abc import abstractmethod
from datetime import datetime
from decimal import Decimal

import scrapy
from scrapy import Selector

from model.action import Action
from model.common.writter import OutputWritter
from model.token_trade import TokenTrade
from scrapping.utils import utils
from scrapping.utils.utils import get_currency_value, parse_time_ago


class HistoryScraper(scrapy.Spider, OutputWritter):
    MAX_NUM_PAGES = 200

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': False
    }

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
    ]

    def __init__(self, base_url, token_adress, index, last_trade_index, es_host, es_port, min_token=0,
                 name='bsc_scrapy', **kwargs):
        super().__init__(name, **kwargs)
        self.base_url = base_url
        self.token_adress = token_adress
        self.es_host = es_host
        self.es_port = es_port
        self.trades = list()
        self.last_saved_trade = None
        self.trades_index = index
        self.last_trade_index = last_trade_index
        self.min_token = min_token
        self.current_page = 1

    def get_headers(self):
        user_agent = self.user_agent_list[random.randint(0, len(self.user_agent_list) - 1)]
        return {'User-Agent': user_agent}

    def start_requests(self):
        urls = []
        for page in range(1, self.MAX_NUM_PAGES + 1):
            urls.append(f'https://bscscan.com/dextracker?q={self.token_adress}&ps=100&p={page}')

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.get_headers())

    @abstractmethod
    def parse(self, response: Selector, **kwargs):
        pass

    def close(self, spider, reason):
        self.save_list_es(self.trades_index, list(self.trades), self.es_host, self.es_port, id_field="txn_hash")
        self.save_raw_es(self.last_trade_index, self.last_saved_trade, self.es_host, self.es_port,
                         id=self.token_adress.lower())
        return super().close(spider, reason)


class BscHistoryScraper(HistoryScraper):

    def parse(self, response: Selector, **kwargs):
        current_time = datetime.now()
        # use set because sometimes trades have the same tx hashs
        trades = list()
        first_trade = True
        for tr in response.xpath("//main[@id='content']//div[contains(@class, 'card')]//tbody/tr"):
            trade = self.get_trade_from_row(current_time, tr, self.token_adress)
            trades.append(trade)

            if first_trade and re.match(r".*p=1$", response.url):
                self.last_saved_trade = trade
            first_trade = False

            self.trades.append(trade)

        for trade in trades:
            txn_url = f'{self.base_url}/tx/{trade.txn_hash}'
            txn_request = scrapy.Request(url=txn_url, callback=self.parse_transaction, cb_kwargs=dict(trade=trade),
                                         headers=self.get_headers(), meta={'dont_redirect': True})
            yield txn_request

    def parse_transaction(self, response, trade):
        owner_adress = response.xpath('//*[@id="addressCopy"]/text()').get()
        value_str = response.xpath('//*[@id="wrapperContent"]/li[1]/div/span[6]/span/text()').get()
        try:
            value = utils.get_currency_value(re.search(r'\$(\d+,)*\d+\.\d+', value_str).group())
            trade.value = value
        except AttributeError as ex:
            logging.error(f'Could not parse {value_str}')
            raise ex
        except TypeError:
            logging.error(f'Could not parse {value_str} at {response.url}')
        trade.owner_adress = owner_adress
        self.trades.append(trade)

    @staticmethod
    def get_trade_from_row(current_time, tr, token_adress):
        columns = tr.xpath(".//td")
        txn_hash = columns[0].xpath('.//text()').get()
        maker_adress = columns[2].xpath('.//a/@href').get().split('/')[-1]
        taker_adress = columns[4].xpath('.//a/@href').get().split('/')[-1]
        amount = Decimal('0')
        amount_out = columns[2].xpath('./text()').get().strip()
        token_out = columns[2].xpath('./a/text()').get().strip()
        amount_in = columns[4].xpath('./text()').get().strip()
        token_in = columns[4].xpath('./a/text()').get().strip()
        if maker_adress.upper() == token_adress.upper():
            action = Action.SELL.value
            amount = Decimal(get_currency_value(columns[2].xpath('.//text()').get()))
        elif taker_adress.upper() == token_adress.upper():
            action = Action.BUY.value
            amount = Decimal(get_currency_value(columns[4].xpath('.//text()').get()))
        else:
            logging.warning('Could not get action type')
            action = Action.UNKNOWN.value
        time_ago_str = columns[1].xpath('.//text()').get()
        trade_date = parse_time_ago(current_time, time_ago_str)

        return TokenTrade(txn_hash=txn_hash, action=action, amount=amount,
                          amount_out=f'{amount_out} {token_out}', amount_in=f'{amount_in} {token_in}',
                          timestamp=trade_date)


class EtherHistoryScraper(HistoryScraper):

    def parse(self, response: Selector, **kwargs):
        raise NotImplementedError
