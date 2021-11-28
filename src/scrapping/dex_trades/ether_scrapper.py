import typing
from decimal import InvalidOperation

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.action import Action
from model.common.utils import processing_time
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import get_currency_value


class EtherScanScrapper(ScanScrapper):
    def __init__(self, token_adress:str, output_format=None, output_path=None) -> None:
        super().__init__(token_adress, output_format, output_path)
        self._base_url = 'https://etherscan.io/'

    @property
    def base_url(self) -> str:
        return self._base_url

    @processing_time()
    def get_trades(self) -> typing.List[TokenTrade]:
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.implicitly_wait(10)
        driver.get(self.get_trades_url(self.token_adress))
        iframe = driver.find_element(By.XPATH, '//*[@id="dextrackeriframe"]')
        driver.switch_to.frame(iframe)
        table = driver.find_element(By.XPATH, '//*[@class="table-responsive"]/table')
        trades = []
        for row in table.find_elements(By.XPATH, './/tbody/tr'):
            columns = row.find_elements(By.XPATH, './/td')
            amount_out = columns[5].text
            amount_in = columns[6].text
            action_str = columns[4].text.upper()
            if action_str == Action.BUY.name:
                action = Action.BUY.value
                amount = get_currency_value(amount_in)
            elif action_str == Action.SELL.name:
                action = Action.SELL.value
                amount = get_currency_value(amount_out)
            else:
                self._logger.warning('Could not get action type')
                action = Action.UNKNOWN.value
                # TODO checker comment ça marche avec une action de type swap
                amount = get_currency_value(amount_in)
            txn_value = -1
            try:
                txn_value = get_currency_value(columns[8].text)
            except InvalidOperation:
                # TODO gérer les cas où txn value est égal à N/A (faire comme pour la bsc, récupérer valeur en live
                #  du token)
                self._logger.error(f'Could not convert to decimal value: {columns[8].text}')

            trade = TokenTrade(txn_hash=columns[1].text, action=action, amount=amount, amount_out=amount_out,
                               amount_in=amount_in, value=txn_value)
            self._logger.debug(f'Trade: {trade}')
            trades.append(trade)

        return trades
