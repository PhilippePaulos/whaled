import logging
import re
from abc import abstractmethod
from datetime import datetime
from decimal import Decimal

import scrapy
from scrapy import Selector

from model.action import Action
from model.common.writter import OutputWritter
from model.token_trade import TokenTradeSaving
from scrapping.utils.utils import get_currency_value, parse_time_ago


class HistoryScraper(scrapy.Spider, OutputWritter):

    MAX_NUM_PAGES = 200

    def __init__(self, token_adress, index, last_trade_index, es_host, es_port, name='bsc_scrapy', **kwargs):
        super().__init__(name, **kwargs)
        self.token_adress = token_adress
        self.es_host = es_host
        self.es_port = es_port
        self.trades = set()
        self.last_saved_trade = None
        self.trades_index = index
        self.last_trade_index = last_trade_index

    def start_requests(self):
        urls = []
        for page in range(1, self.MAX_NUM_PAGES + 1):
            urls.append(f'https://bscscan.com/dextracker?q={self.token_adress}&ps=100&p={page}')

        hdr = {'User-Agent': 'Mozilla/5.0'}
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=hdr)

    @abstractmethod
    def parse(self):
        pass

    def close(self, spider, reason):
        self.save_list_es(self.trades_index, list(self.trades), self.es_host, self.es_port, id_field="txn_hash")
        self.save_raw_es(self.last_trade_index, self.last_saved_trade, self.es_host, self.es_port,
                         id=self.token_adress.lower())
        return super().close(spider, reason)


class BscHistoryScraper(HistoryScraper):

    def parse(self, response: Selector, **kwargs):
        current_time = datetime.now()
        trades = set()
        first_trade = True
        for tr in response.xpath("//main[@id='content']//div[contains(@class, 'card')]//tbody/tr"):
            columns = tr.xpath(".//td")
            txn_hash = columns[0].xpath('.//text()').get()
            maker_adress = columns[2].xpath('.//a/@href').get().split('/')[-1]
            taker_adress = columns[4].xpath('.//a/@href').get().split('/')[-1]
            amount = Decimal('0')
            amount_out = columns[2].xpath('./text()').get().strip()
            token_out = columns[2].xpath('./a/text()').get().strip()
            amount_in = columns[4].xpath('./text()').get().strip()
            token_in = columns[4].xpath('./a/text()').get().strip()

            if maker_adress.upper() == self.token_adress.upper():
                action = Action.SELL.value
                amount = Decimal(get_currency_value(columns[2].xpath('.//text()').get()))
            elif taker_adress.upper() == self.token_adress.upper():
                action = Action.BUY.value
                amount = Decimal(get_currency_value(columns[4].xpath('.//text()').get()))
            else:
                logging.warning('Could not get action type')
                action = Action.UNKNOWN.value
            time_ago_str = columns[1].xpath('.//text()').get()
            trade_date = parse_time_ago(current_time, time_ago_str)

            trade = TokenTradeSaving(txn_hash=txn_hash, action=action, amount=amount,
                                     amount_out=f'{amount_out} {token_out}', amount_in=f'{amount_in} {token_in}',
                                     timestamp=trade_date)

            trades.add(trade)

            if first_trade and re.match(r".*p=1$", response.url):
                self.last_saved_trade = trade
            first_trade = False

        self.trades.update(trades)


class EtherHistoryScraper(HistoryScraper):

    def parse(self, response: Selector, **kwargs):
        raise NotImplementedError
