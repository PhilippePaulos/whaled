import logging
import re
from abc import abstractmethod
from datetime import datetime

import scrapy
from scrapy import Selector

from model.common.writter import OutputWritter
from scrapping.dex_trades import scan_helper
from scrapping.utils import utils
from scrapping.utils.utils import get_headers


class HistoryScraper(scrapy.Spider, OutputWritter):
    MAX_NUM_PAGES = 1

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'COOKIES_ENABLED': False
    }

    def __init__(self, base_url, token_adress, index, last_trade_index, tr_xpath, es_host, es_port, min_token=0,
                 name='bsc_scrapy', **kwargs):
        super().__init__(name, **kwargs)
        self.token_adress = token_adress
        self.es_host = es_host
        self.es_port = es_port
        self.trades = list()
        self.last_saved_trade = None
        self.trades_index = index
        self.last_trade_index = last_trade_index
        self.min_token = min_token
        self.current_page = 1
        self.base_url = base_url
        self.tr_xpath = tr_xpath

    @property
    @abstractmethod
    def blockchain(self):
        pass

    def start_requests(self):
        urls = self.get_all_pages()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=get_headers())

    # TODO stop scrapping when last_trade found
    def parse(self, response: Selector, **kwargs):
        current_time = datetime.now()
        # use set because sometimes trades have the same tx hashs
        trades = list()
        first_trade = True
        for tr in response.xpath(self.tr_xpath):
            trade = scan_helper.get_trade_from_row(current_time, tr, self.token_adress, chain=self.blockchain)
            trades.append(trade)
            if first_trade and re.match(r".*p=1$", response.url):
                self.last_saved_trade = trade
            first_trade = False
        for trade in trades:
            txn_url = f'{self.base_url}/tx/{trade.txn_hash}'
            txn_request = scrapy.Request(url=txn_url, callback=self.parse_transaction, cb_kwargs=dict(trade=trade),
                                         headers=get_headers(), meta={'dont_redirect': True})
            yield txn_request

    @abstractmethod
    def parse_transaction(self, response, trade):
        pass

    def close(self, spider, reason):
        self.save_list_es(self.trades_index, list(self.trades), self.es_host, self.es_port, id_field="txn_hash")
        self.save_raw_es(self.last_trade_index, self.last_saved_trade, self.es_host, self.es_port,
                         id=self.token_adress.lower())
        return super().close(spider, reason)

    @abstractmethod
    def get_all_pages(self):
        pass


class BscHistoryScraper(HistoryScraper):

    @property
    def blockchain(self):
        return 'bsc'

    def get_all_pages(self):
        for page in range(1, self.MAX_NUM_PAGES + 1):
            yield f"https://bscscan.com/dextracker?q={self.token_adress}&p={page}"

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


class EtherHistoryScraper(HistoryScraper):

    @property
    def blockchain(self):
        return 'ether'

    def get_all_pages(self):
        for page in range(1, self.MAX_NUM_PAGES + 1):
            yield f"{self.base_url}dextracker_txns?q={self.token_adress}&p={page}"

    def parse_transaction(self, response, trade):
        owner_adress = response.xpath('//*[@id="addressCopy"]/text()').get()
        trade.owner_adress = owner_adress
        self.trades.append(trade)
