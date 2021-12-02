import logging
import time
import typing
from abc import abstractmethod

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from model.common.output import OutputFormats
from model.common.singleton import Singleton
from model.common.utils import processing_time
from model.token_trade import TokenTrade
from scrapping.currency.currency_scrapper import OutputWritter


class DriverInstance(metaclass=Singleton):
    __logger = logging.getLogger()

    def __init__(self, url: str):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=s)
        self.driver.implicitly_wait(10)
        self.driver.get(url)


class ScanScrapper(OutputWritter):
    MAX_NUM_TRADES = 100

    def __init__(self, token_adress: str, check_interval=None, output_format=None, output_path=None) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress
        self.driver_instance = DriverInstance(self.get_trades_url())
        self.check_interval = check_interval
        self.output_format = output_format
        self.output_path = output_path

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    def get_trades_url(self) -> str:
        pass

    def process(self, history):
        if history:
            trades = self.get_trades_history()
            self.save(trades)
        else:
            while True:
                trades = self.get_last_trades()
                self.save(trades)
                self._logger.info(f'waiting (check interval={self.check_interval})...')
                time.sleep(self.check_interval)

    @processing_time()
    def get_last_trades(self) -> typing.List[TokenTrade]:
        return self.get_trades_from_page()

    @abstractmethod
    def get_trades_from_page(self):
        pass

    def get_trades_history(self) -> typing.List[TokenTrade]:
        trades = []
        current_page = 1
        last_page = self.get_last_page_number()
        while current_page != last_page + 1:
            trades.extend(self.get_trades_from_page())
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

    def save(self, trades):
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            self.save_csv(self.output_path, trades)
        else:
            raise NotImplemented(self.output_format)
