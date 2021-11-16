import typing
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import processing_time


class BscScanScrapper(ScanScrapper):

    def __init__(self) -> None:
        super().__init__()
        self._base_url = 'https://bscscan.com/'

    @property
    def base_url(self) -> str:
        return self._base_url

    @processing_time()
    def get_trades(self, token_adress: str) -> typing.List[TokenTrade]:
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.implicitly_wait(10)
        driver.get(self.get_trades_url(token_adress))
        iframe = driver.find_element(By.XPATH, '//*[@id="dextrackeriframe"]')
        driver.switch_to.frame(iframe)

        table = driver.find_element(By.XPATH, '//*[@class="table-responsive"]/table')

        trades = []
        for row in table.find_elements(By.XPATH, './/tbody/tr'):
            columns = row.find_elements(By.XPATH, './/td')
            maker_adress = columns[3].find_element(By.XPATH, './/a').get_attribute('href').split('/')[-1]
            taker_adress = columns[5].find_element(By.XPATH, './/a').get_attribute('href').split('/')[-1]
            if maker_adress == token_adress:
                action = Action.SELL
            elif taker_adress == token_adress:
                action = Action.BUY
            else:
                self._logger.warning('Could not get action type')
                action = Action.UNKNOWN
            # TODO get currency value from bogged scrapper (in different thread)
            trade = TokenTrade(txn_hash=columns[0].text, action=action, amount_out=columns[3].text,
                               amount_in=columns[5].text, value=Decimal('0'))
            self._logger.debug(f'trade: {trade}')
            trades.append(trade)
        return trades
