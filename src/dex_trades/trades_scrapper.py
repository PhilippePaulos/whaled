import logging
import time
import typing
from abc import abstractmethod
from datetime import datetime
from typing import Optional, Tuple, List

import requests
from elasticsearch import Elasticsearch
from scrapy import Selector
from scrapy.crawler import CrawlerProcess

from model.common.utils import processing_time
from model.common.writter import OutputWritter
from model.token_trade import TokenTrade
from dex_trades.scan_helper import get_trade_from_row
from dex_trades.trades_config import TradesConfig
from utils.utils import get_headers


class ScanScrapper(OutputWritter):
    MAX_NUM_TRADES = 100

    def __init__(self, token_adress: str) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress
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

    @property
    @abstractmethod
    def tr_xpath(self):
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

    @processing_time()
    def get_new_trades(self, last_checked_trade_hash) -> Tuple[List[TokenTrade], str]:
        if last_checked_trade_hash is None:
            last_checked_trade_hash = self.get_last_checked_transaction_hash()
        trades = self.get_trades_from_page(last_checked_trade_hash)
        if len(trades) == 0:
            return trades, last_checked_trade_hash
        else:
            last_checked_trade = trades[0]
            return trades, last_checked_trade.txn_hash

    def save_last_checked_trade(self, token_trade: TokenTrade):
        self.save_raw_es(self.last_checked_trade_index, token_trade, self.es_host, self.es_port,
                         id=self.token_adress.lower())

    def get_trades_from_page(self, last_trade_txn=None) -> typing.List[TokenTrade]:
        """
        Get ordered trades, stops if last_trade_txn matches a txn from the page
        :param last_trade_txn:
        :return: List of TokenTrade
        """
        # TODO get trades from next pages until last_trade found
        current_time = datetime.now()
        trades = []
        response = requests.get(self.get_trades_url(), headers=get_headers())

        for tr in Selector(response).xpath(self.tr_xpath):
            # todo utiliser set pour virer les tx doublons
            trade = get_trade_from_row(current_time, tr, self.token_adress, chain='ether')
            if trade.txn_hash == last_trade_txn:
                self._logger.info(f'{trade.txn_hash} already saved')
                self._logger.info('Complete transaction fetching...')
                return trades
            self._logger.debug(f'trade: {trade}')
            trades.append(trade)
        return trades

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

    def save(self, trades):
        self.save_list_es(self.es_index, trades, self.es_host, self.es_port)

    @staticmethod
    def filter_trades(trade: TokenTrade):
        if trade.amount >= int(TradesConfig().filter_num_tokens):
            return True
        return False

    def save_trades_history(self):
        process = CrawlerProcess()
        process.crawl(self.history_module, base_url=self.base_url, min_token=TradesConfig().filter_num_tokens,
                      token_adress=self.token_adress, tr_xpath=self.tr_xpath, index=self.es_index,
                      last_trade_index=self.last_checked_trade_index, es_host=self.es_host, es_port=self.es_port)

        process.start()
