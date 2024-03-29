import logging
import os
import time
from datetime import datetime
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from model.common.singleton import Singleton
from model.token_info import TokenInfo
from currency.currency_scrapper import CurrencyScrapper
from utils import utils


class ChartInstance(metaclass=Singleton):
    __logger = logging.getLogger()

    def __init__(self, url: str, load_marketcap=True):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=s)
        self.load_chart(url, load_marketcap)

    def load_chart(self, url, load_marketcap=True):
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        while utils.get_currency_value(self.get_price_str()) == Decimal('0'):
            self.__logger.info('Waiting price loading')
            time.sleep(1)
        if load_marketcap:
            while utils.get_currency_value(self.get_market_cap()) == Decimal('0'):
                self.__logger.info('Waiting marketcap loading')
                time.sleep(1)

    def get_price_str(self):
        return self.driver.find_element(By.XPATH,
                                        '//*[@id="headlessui-listbox-button-8"]/div/div[2]/h4[1]').text

    def get_market_cap(self):
        w = WebDriverWait(self.driver, 30)
        m_cap_element = w.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="chartWrapper"]/div[1]/div[2]/div[2]/div[3]/span[2]/h4')))
        return m_cap_element.text


class BoggedScrapper(CurrencyScrapper):

    def __init__(self, token_adress: str, load_marketcap=True) -> None:
        super().__init__(token_adress)
        self.base_url = 'https://beta.bogged.finance/?c=bsc'
        self.chart_instance = ChartInstance(self.get_token_url(self.token_adress), load_marketcap)

    def get_token_info(self, token_adress, load_marketcap=True) -> TokenInfo:
        if self.token_adress != token_adress:
            self.chart_instance.load_chart(self.get_token_url(token_adress))
        m_cap = None
        if load_marketcap:
            m_cap = self.get_currency_mcap()
        token_info = TokenInfo(utils.get_currency_value(self.chart_instance.get_price_str()), m_cap, datetime.now())
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
        return os.path.join(f"{self.base_url}&t={token_adress}")
