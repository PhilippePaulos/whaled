import logging
import os
from datetime import datetime
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.common.singleton import Singleton
from model.token_price import TokenPrice
from scrapping.currency_prices.currency_scrapper import CurrencyScrapper
from scrapping.utils import utils


class ChartInstance(metaclass=Singleton):

    _logger = logging.getLogger()

    def __init__(self, url: str):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.get(url)
        driver.implicitly_wait(10)
        self.driver = driver
        while utils.get_currency_value(self.get_price_str()) == Decimal('0'):
            self._logger.info('Waiting price loading')

    def get_price_str(self):
        return self.driver.find_element(By.XPATH,
                                        '//*[@id="chartWrapper"]/div[1]/div[1]/div[1]/div[1]/span/span/div[1]/h4').text


class BoggedScrapper(CurrencyScrapper):

    def __init__(self) -> None:
        super().__init__()
        self.base_url = 'https://charts.bogged.finance'

    def get_currency_price(self, token_adress: str) -> TokenPrice:
        chart_instance = ChartInstance(self.get_token_url(token_adress))
        token_price = TokenPrice(utils.get_currency_value(chart_instance.get_price_str()),
                                 datetime.now())
        logging.info(token_price)
        return token_price

    def get_token_url(self, token_adress: str) -> str:
        return os.path.join(f"{self.base_url}/{token_adress}")
