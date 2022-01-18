import logging
import time
import typing
from abc import abstractmethod
from typing import Optional, Tuple, List

import webdriver_manager.firefox
from elasticsearch import Elasticsearch
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from model.common.singleton import Singleton
from model.common.utils import processing_time
from model.common.writter import OutputWritter
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_config import TradesConfig


class DriverInstance(metaclass=Singleton):
    __logger = logging.getLogger()

    def __init__(self, url: str):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=s)
        self.driver.implicitly_wait(10)
        self.driver.get(url)


class ScanScrapper(OutputWritter):
    MAX_NUM_TRADES = 100

    def __init__(self, token_adress: str) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress
        self.driver_instance = DriverInstance(self.get_trades_url())
        self.check_interval = TradesConfig().check_interval
        self.es_host = TradesConfig().es_host
        self.es_port = TradesConfig().es_port

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    @abstractmethod
    def history_module(self):
        pass

    @abstractmethod
    def get_trades_url(self) -> str:
        pass

    @property
    def es_index(self) -> str:
        return f'trades-{self.token_adress}'.lower()

    @property
    def last_checked_trade_index(self) -> str:
        return f'last_checked_trades'

    def process(self, history):
        if history:
            self.save_trades_history()
        else:
            last_checked_trade = None
            while True:
                trades, last_checked_trade = self.get_new_trades(last_checked_trade)
                trades = list(filter(self.filter_trades, trades))
                self.save(trades)
                if len(trades) > 0:
                    self.save_last_checked_trade(trades[0])
                self._logger.info(f'waiting (check interval={self.check_interval})...')
                time.sleep(self.check_interval)
                self.reload_page()

    @processing_time()
    def get_new_trades(self, last_checked_trade_hash) -> Tuple[List[TokenTrade], str]:
        token_trades = []
        if last_checked_trade_hash is None:
            last_checked_trade_hash = self.get_last_checked_transaction_hash()
        if last_checked_trade_hash is not None:
            changed_page = False
            while True:
                tokens, match = self.get_trades_from_page(last_checked_trade_hash)
                token_trades.extend(tokens)

                if match and len(tokens) == 0:
                    return tokens, last_checked_trade_hash
                elif match and len(tokens) > 0:
                    last_checked_trade = token_trades[0]
                    if changed_page:
                        self.driver_instance.driver.get(self.get_trades_url())
                    return token_trades, last_checked_trade.txn_hash
                else:
                    self.move_to_next_page()
                    changed_page = True
        else:
            token_trades, _ = self.get_trades_from_page()
            return token_trades, token_trades[0].txn_hash

    def save_last_checked_trade(self, token_trade: TokenTrade):
        self.save_raw_es(self.last_checked_trade_index, token_trade, self.es_host, self.es_port,
                         id=self.token_adress.lower())

    @abstractmethod
    def get_trades_from_page(self, last_trade_txn=None) -> typing.Tuple[typing.List[TokenTrade], bool]:
        """
        Get trades ordered trades from current browser page, stops if last_trade_txn matches a txn from the page
        :param last_trade_txn:
        :return: tuple of TokenTrade list with boolean to True if last_trade_txn has been matched, False otherwise
        """
        pass

    def get_last_checked_transaction_hash(self) -> Optional[str]:
        es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
        query = '{"query": {"terms": {"_id": ["' + self.token_adress.lower() + '"]}}}'
        try:
            last_trade = es.search(index=self.last_checked_trade_index,
                                   body=query)['hits']['hits'][0]['_source']['txn_hash']
            return last_trade
        except IndexError:
            self._logger.info(f"{self.es_index} doesn't exists. There is no transactions yet")
            return None

    @abstractmethod
    def move_to_next_page(self):
        pass

    def save(self, trades):
        self.save_list_es(self.es_index, trades, self.es_host, self.es_port)

    def reload_page(self):
        self.driver_instance.driver.refresh()

    @staticmethod
    def filter_trades(trade: TokenTrade):
        if trade.amount >= int(TradesConfig().filter_num_tokens):
            return True
        return False

    def save_trades_history(self):
        process = CrawlerProcess()
        process.crawl(self.history_module, base_url=self.base_url, min_token=TradesConfig().filter_num_tokens,
                      token_adress=self.token_adress, index=self.es_index,
                      last_trade_index=self.last_checked_trade_index, es_host=self.es_host, es_port=self.es_port)

        process.start()
