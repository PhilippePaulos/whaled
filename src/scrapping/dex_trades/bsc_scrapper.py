import typing
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.action import Action
from model.common.utils import processing_time
from model.token_trade import TokenTrade
from scrapping.currency.bogged_scrapper import BoggedScrapper
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import get_currency_value


class BscScanScrapper(ScanScrapper):

    def __init__(self, token_adress: str, output_format=None, output_path=None) -> None:
        super().__init__(token_adress, output_format, output_path)
        self._base_url = 'https://bscscan.com/'

    @property
    def base_url(self) -> str:
        return self._base_url

    @processing_time()
    def get_trades(self) -> typing.List[TokenTrade]:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.get_token_info, self.token_adress),
                executor.submit(self.get_trades_from_html, self.token_adress)
            ]
            token_info = futures[0].result()
            trades: typing.List[TokenTrade] = futures[1].result()
        for trade in trades:
            trade.value = token_info.price * trade.amount
        return trades

    def get_trades_from_html(self, token_adress) -> typing.List[TokenTrade]:
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
            amount = Decimal('0')
            if maker_adress == token_adress:
                action = Action.SELL.value
                amount = Decimal(get_currency_value(columns[3].text))
            elif taker_adress == token_adress:
                action = Action.BUY.value
                amount = Decimal(get_currency_value(columns[5].text))
            else:
                self._logger.warning('Could not get action type')
                action = Action.UNKNOWN.value
            trade = TokenTrade(txn_hash=columns[0].text, action=action, amount=amount, amount_out=columns[3].text,
                               amount_in=columns[5].text)
            self._logger.debug(f'trade: {trade}')
            trades.append(trade)
        return trades

    @staticmethod
    def get_token_info(token_adress):
        token_price = BoggedScrapper(token_adress, load_marketcap=False).get_token_info()
        return token_price
