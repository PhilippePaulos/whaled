import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import get_currency_value, processing_time


class EtherScanScrapper(ScanScrapper):
    def __init__(self) -> None:
        super().__init__()
        self._base_url = 'https://etherscan.io/'

    @property
    def base_url(self):
        return self._base_url

    @processing_time()
    def get_trades(self, token_adress: str):
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
            action = Action.BUY.value if columns[4].text == Action.BUY else Action.SELL
            trade = TokenTrade(txn_hash=columns[1].text, action=action, amount_out=columns[5].text,
                                     amount_in=columns[6].text, value=get_currency_value(columns[8].text))
            self._logger.debug(f'trade: {trade}')
            trades.append(trade)
        return trades


if __name__ == '__main__':
    print(EtherScanScrapper().get_trades('0xB8c77482e45F1F44dE1745F52C74426C631bDD52'))