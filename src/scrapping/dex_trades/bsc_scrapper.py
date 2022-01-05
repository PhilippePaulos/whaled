import concurrent.futures
import typing
from datetime import datetime
from decimal import Decimal
from typing import Tuple, List

from selenium.webdriver.common.by import By

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.currency.bogged_scrapper import BoggedScrapper
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import get_currency_value


class BscScanScrapper(ScanScrapper):

    def __init__(self, token_adress: str) -> None:
        super().__init__(token_adress)

    @property
    def base_url(self) -> str:
        return 'https://bscscan.com'
    
    def get_trades_url(self) -> str:
        return f'{self.base_url}/dextracker?q={self.token_adress}&ps={self.MAX_NUM_TRADES}'

    def get_trades_with_price(self, price, last_trade_txn=None, disable_price_check=False) -> \
            Tuple[List[TokenTrade], bool, Decimal]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.get_trades_from_page, last_trade_txn)]
            if price is None and not disable_price_check:
                futures.append(executor.submit(self.get_token_info))
                token_info = futures[1].result()
            trades: typing.List[TokenTrade] = futures[0].result()[0]
            match = futures[0].result()[1]
        if not disable_price_check:
            if price is None:
                price = token_info.price
            for trade in trades:
                trade.value = price * trade.amount
        return trades, match, price

    def get_trades_from_page(self, last_trade_txn=None) -> typing.Tuple[typing.List[TokenTrade], bool, bool]:
        driver = self.driver_instance.driver
        table = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[2]/table')
        trades = []
        current_time = datetime.now()
        for row in table.find_elements(By.XPATH, './/tbody/tr'):
            columns = row.find_elements(By.XPATH, './/td')
            maker_adress = columns[2].find_element(By.XPATH, './/a').get_attribute('href').split('/')[-1]
            taker_adress = columns[4].find_element(By.XPATH, './/a').get_attribute('href').split('/')[-1]
            amount = Decimal('0')
            if maker_adress.upper() == self.token_adress.upper():
                action = Action.SELL.value
                amount = Decimal(get_currency_value(columns[2].text))
            elif taker_adress.upper() == self.token_adress.upper():
                action = Action.BUY.value
                amount = Decimal(get_currency_value(columns[4].text))
            else:
                self._logger.warning('Could not get action type')
                action = Action.UNKNOWN.value
            time_ago_str = columns[1].text
            trade_date = ScanScrapper.parse_time_ago(current_time, time_ago_str)
            trade = TokenTrade(txn_hash=columns[0].text, action=action, amount=amount, amount_out=columns[2].text,
                               amount_in=columns[4].text, timestamp=trade_date)
            if last_trade_txn is not None and trade.txn_hash == last_trade_txn:
                self._logger.info(f'{trade.txn_hash} already saved')
                self._logger.info('Complete transaction fetching...')
                return trades, True, False
            self._logger.debug(f'trade: {trade}')
            trades.append(trade)
        empty_page = False
        if len(trades) == 0:
            empty_page = True
        return trades, False, empty_page

    def get_token_info(self):
        return BoggedScrapper(self.token_adress, load_marketcap=False).get_token_info(self.token_adress,
                                                                                      load_marketcap=False)

    def get_last_page_number(self) -> int:
        last_page = int(
            self.driver_instance.driver.find_element(By.XPATH, '//*[@id="ctl00"]/div[3]/ul/li[3]/span/strong[2]').text)
        return last_page

    def move_to_next_page(self):
        next_page_link_element = self.driver_instance.driver.find_element(By.XPATH,
                                                                  '//*[@id="content"]/div[2]/div/div[2]/div[1]/nav/ul/li[4]/a')
        self.driver_instance.driver.execute_script("arguments[0].scrollIntoView(true);", next_page_link_element)
        next_page_link_element.click()
