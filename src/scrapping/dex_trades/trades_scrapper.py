import logging
import os
import time
import typing
from abc import abstractmethod
from decimal import Decimal
from typing import Optional, Tuple, List

import webdriver_manager.firefox
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from model.common.output import OutputFormats
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
        self.output_format = TradesConfig().output_format
        self.output_path = TradesConfig().output_path
        self.es_host = TradesConfig().es_host
        self.es_port = TradesConfig().es_port

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    def get_trades_url(self) -> str:
        pass

    @property
    def es_index(self) -> str:
        return f'trades-{self.token_adress}'.lower()

    def process(self, history):
        if history:
            trades = self.get_trades_history()
            trades = list(filter(self.filter_trades, trades))
            self.save(trades)
        else:
            last_trade = None
            while True:
                trades, last_trade = self.get_new_trades(last_trade)
                trades = list(filter(self.filter_trades, trades))
                self.save(trades, prepend=True)
                self._logger.info(f'waiting (check interval={self.check_interval})...')
                time.sleep(self.check_interval)
                self.reload()

    @processing_time()
    def get_new_trades(self, last_trade) -> Tuple[List[TokenTrade], str]:
        token_trades = []
        if last_trade is None:
            last_trade = self.get_last_saved_transaction()
        if last_trade is not None:
            token_price: Optional[Decimal] = None
            while True:
                tokens, match, token_price = self.get_trades_with_price(token_price, last_trade_txn=last_trade,
                                                                        disable_price_check=TradesConfig().disable_price_check)
                token_trades.extend(tokens)
                if match and len(tokens) == 0:
                    return tokens, last_trade
                elif match and len(tokens) > 0:
                    return token_trades, tokens[0].txn_hash
                else:
                    self.move_to_next_page()
        else:
            token_trades, _, _ = self.get_trades_with_price(None,
                                                            disable_price_check=TradesConfig().disable_price_check)
            return token_trades, token_trades[0].txn_hash

    def get_trades_with_price(self, price, last_trade_txn=None, disable_price_check=False) ->\
            Tuple[List[TokenTrade], bool, Decimal]:
        tokens, match = self.get_trades_from_page(last_trade_txn)
        return tokens, match, price

    @abstractmethod
    def get_trades_from_page(self, last_trade_txn=None) -> typing.Tuple[typing.List[TokenTrade], bool]:
        """
        Get trades ordered trades from current browser page, stops if last_trade_txn matches a txn from the page
        :param last_trade_txn:
        :return: tuple of TokenTrade list with boolean to True if last_trade_txn has been matched, False otherwise
        """
        pass

    def get_csv_output_path(self):
        return os.path.join(self.output_path, f'token_trades_{self.token_adress}.csv')

    def get_last_saved_transaction(self) -> Optional[str]:
        """
        Gets the last saved transaction from CSV or ES
        :return: last saved transaction or None
        """
        self._logger.info('Getting last saved transaction...')
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            if os.path.exists(self.get_csv_output_path()):
                with open(self.get_csv_output_path(), "r") as file:
                    # last txn is at first file line
                    first_line = file.readline()
                    return first_line.split(';')[0]
            else:
                self._logger.warning(f"Couldn't find previous csv trades file at {self.get_csv_output_path()}")
        elif self.output_format.upper() == OutputFormats.OUTPUT_ES:
            es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
            query = '{"query": {"match_all":{}},"size": 1,"sort": [{"timestamp": {"order": "desc"}}]}'
            try:
                last_trade = es.search(index=self.es_index, body=query)['hits']['hits'][0]['_source']['txn_hash']
                return last_trade
            except NotFoundError:
                self._logger.info(f"{self.es_index} doesn't exists. There is no transactions yet")
                return None
        else:
            self._logger.error('Cannot get last transaction, output_format not supported.')
            return None

    @processing_time()
    def get_trades_history(self) -> typing.List[TokenTrade]:
        trades = []
        current_page = 1
        last_page = self.get_last_page_number()
        while current_page != last_page + 1:
            trades.extend(self.get_trades_from_page()[0])
            self._logger.debug(f'Moving to next page ({current_page + 1})')
            self.move_to_next_page()
            current_page += 1
        return trades

    @abstractmethod
    def get_last_page_number(self) -> int:
        pass

    @abstractmethod
    def move_to_next_page(self):
        pass

    def save(self, trades, prepend=False):
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            self.save_csv(os.path.join(self.output_path, f'token_trades_{self.token_adress}.csv'), trades, prepend)
        elif self.output_format.upper() == OutputFormats.OUTPUT_ES:
            self.save_es(self.es_index, trades, self.es_host, self.es_port)
        else:
            raise NotImplemented(self.output_format)

    def reload(self):
        self.driver_instance.driver.refresh()

    @staticmethod
    def filter_trades(trade: TokenTrade):
        if trade.amount >= int(TradesConfig().filter_num_tokens):
            return True
        return False
