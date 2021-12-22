from datetime import datetime
from decimal import InvalidOperation
from telnetlib import EC
from typing import Tuple, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import get_currency_value


class EtherScanScrapper(ScanScrapper):

    def __init__(self, token_adress:str) -> None:
        super().__init__(token_adress)
        self.prepare_page()

    def reload(self):
        self.driver_instance.driver.refresh()
        self.prepare_page()

    def prepare_page(self):
        iframe = self.driver_instance.driver.find_element(By.XPATH, '//*[@id="txnsiframe"]')
        self.driver_instance.driver.switch_to.frame(iframe)
        wait = WebDriverWait(self.driver_instance.driver, 10)
        # wait until overlay is invisible so we can click on the select element
        wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="overlay"]')))
        select_element = self.driver_instance.driver.find_element(By.XPATH, '//*[@id="ddlRecordsPerPage"]')
        Select(select_element).select_by_value(str(self.MAX_NUM_TRADES))

    @property
    def base_url(self) -> str:
        return 'https://etherscan.io/'

    def get_trades_url(self) -> str:
        return f'{self.base_url}dex?q={self.token_adress}#transactions'

    def get_trades_from_page(self, last_trade_txn=None) -> Tuple[List[TokenTrade], bool]:
        table = self.driver_instance.driver.find_element(By.XPATH, '//*[@id="doneloadingframe"]/div[3]/table')
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
                               amount_in=amount_in, value=txn_value, timestamp=datetime.now().timestamp())
            if last_trade_txn is not None and trade.txn_hash == last_trade_txn:
                self._logger.info(f'{trade.txn_hash} already saved')
                self._logger.info('End transaction fetching...')
                return trades, True
            self._logger.debug(f'Trade: {trade}')
            trades.append(trade)
        return trades, False

    def move_to_next_page(self):
        next_page_link_element = self.driver_instance.driver.find_element(By.XPATH,
                                                                  '//*[@id="doneloadingframe"]/div[2]/nav/ul/li[4]/a')
        self.driver_instance.driver.execute_script("arguments[0].scrollIntoView(true);", next_page_link_element)
        next_page_link_element.click()

    def get_last_page_number(self) -> int:
        last_page = int(
            self.driver_instance.driver.find_element(By.XPATH, '//*[@id="ctl07"]/div[3]/ul/li[3]/span/strong[2]').text)
        return last_page
