import logging
from decimal import Decimal

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_scrapper import ScanScrapper


class BscScanScrapper(ScanScrapper):

    def __init__(self) -> None:
        super().__init__()
        self._base_url = 'https://bscscan.com/'

    @property
    def base_url(self):
        return self._base_url

    def get_trades(self, token_adress: str):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.get(self.get_trades_url(token_adress))
        iframe = driver.find_element(By.XPATH, '//*[@id="dextrackeriframe"]')
        wait = WebDriverWait(driver, 10)
        wait.until(EC.frame_to_be_available_and_switch_to_it(iframe))
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
                #TODO create log factory
                logging.Logger.warning('could not get action type')
                action = Action.UNKNOWN
            # TODO get currency value from API (coingecko, marketcap, pancaswap...)
            # We need to find a way to get price of shitcoins not listed in coingecko/marketcap
            # Tried pancakeswap but price is not aligned with coingecko:
            # https://api.pancakeswap.info/api/v2/tokens/0x2859e4544c4bb03966803b044a93563bd2d0dd4d
            # try moralis api https://www.youtube.com/watch?v=bjJlluIHQAg
            trades.append(TokenTrade(txn_hash=columns[0].text, action=action, amount_out=columns[3].text,
                                     amount_in=columns[5].text, value=Decimal('0')))
        return trades
