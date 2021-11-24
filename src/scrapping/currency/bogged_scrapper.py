import logging
import os
import time
from datetime import datetime
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.common.singleton import Singleton
from model.token_info import TokenInfo
from scrapping.currency.currency_scrapper import CurrencyScrapper
from scrapping.utils import utils


class ChartInstance(metaclass=Singleton):
    __logger = logging.getLogger()

    def __init__(self, url: str, load_marketcap=True):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.get(url)
        driver.implicitly_wait(10)
        self.driver = driver
        while utils.get_currency_value(self.get_price_str()) == Decimal('0'):
            self.__logger.info('Waiting price loading')
            time.sleep(1)
        if load_marketcap:
            while utils.get_currency_value(self.get_market_cap()) == Decimal('0'):
                self.__logger.info('Waiting marketcap loading')
                time.sleep(1)

    def get_price_str(self):
        return self.driver.find_element(By.XPATH,
                                        '//*[@id="chartWrapper"]/div[1]/div[1]/div[1]/div[1]/span/span/div[1]/h4').text

    def get_market_cap(self):
        return self.driver.find_element(By.XPATH, '//*[@id="chartWrapper"]/div[1]/div/div[1]/div[2]/span[3]/h4').text


class BoggedScrapper(CurrencyScrapper):

    def __init__(self, token_adress, load_marketcap=True) -> None:
        super().__init__(token_adress)
        self.base_url = 'https://charts.bogged.finance'
        self.chart_instance = ChartInstance(self.get_token_url(self.token_adress), load_marketcap)

    def get_token_info(self) -> TokenInfo:
        token_info = TokenInfo(utils.get_currency_value(self.chart_instance.get_price_str()), self.get_currency_mcap(),
                               datetime.now())
        self._logger.info(token_info)
        return token_info

    def get_currency_price(self) -> Decimal:
        return utils.get_currency_value(self.chart_instance.get_price_str())

    def get_currency_mcap(self) -> Decimal:
        market_cap_str = self.chart_instance.get_market_cap()
        value = utils.get_currency_value(market_cap_str)
        if market_cap_str[-1] == 'M':
            value = value * 1000000
        elif market_cap_str[-1] == 'B':
            value = value * 1000000000
        return value

    def get_token_url(self, token_adress: str) -> str:
        return os.path.join(f"{self.base_url}/{token_adress}")
