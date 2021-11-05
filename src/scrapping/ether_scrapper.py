import sys

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from model.action import Action
from model.token_trade import TokenTrade
from scrapper import ScanScrapper
from utils.utils import get_currency_value


class EtherScanScrapper(ScanScrapper):

    def get_trades(self, url: str):
        s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
        driver.get(url)
        iframe = driver.find_element(By.XPATH, '//*[@id="dextrackeriframe"]')
        wait = WebDriverWait(driver, 10)
        wait.until(EC.frame_to_be_available_and_switch_to_it(iframe))

        table = driver.find_element(By.XPATH, '//*[@class="table-responsive"]/table')
        trades = []
        for row in table.find_elements(By.XPATH, './/tbody/tr'):
            columns = row.find_elements(By.XPATH, './/td')
            action = Action.BUY.value if columns[4].text == Action.BUY else Action.SELL
            trades.append(TokenTrade(txn_hash=columns[1].text, action=action, amount_out=columns[5].text,
                                     amount_in=columns[6].text, value=get_currency_value(columns[8].text)))
        return trades


if __name__ == '__main__':
    # get_trades('https://etherscan.io/token/0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3#tokenTrade')
    sys.exit(0)
