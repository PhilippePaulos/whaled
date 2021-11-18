import os
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.common.singleton import Singleton
from scrapping.currency_prices.currency_scrapper import CurrencyScrapper
from scrapping.utils import utils


class ChartInstance(metaclass=Singleton):

    def __init__(self, url: str):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.get(url)
        driver.implicitly_wait(10)
        self.chart = driver.find_element(By.XPATH, '//*[@id="chartWrapper"]')


class BoggedScrapper(CurrencyScrapper):

    def __init__(self) -> None:
        super().__init__()
        self.base_url = 'https://charts.bogged.finance'

    def get_currency_price(self, token_adress: str) -> Decimal:
        chart_instance = ChartInstance(self.get_token_url(token_adress))
        # TODO wait element to be clickable
        token_price_str = chart_instance.chart.find_element(By.XPATH,
                                     '//*[@id="chartWrapper"]/div[1]/div[1]/div[1]/div[1]/span/span/div[1]/h4').text
        return utils.get_currency_value(token_price_str)

    def get_token_url(self, token_adress: str) -> str:
        return os.path.join(f"{self.base_url}/{token_adress}")


if __name__ == '__main__':
    BoggedScrapper().get_currency_price('0x9D12CC56d133Fc5c60E9385B7A92F35a682da0bd')
