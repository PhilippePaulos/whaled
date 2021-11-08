import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.trades_scrapper import ScanScrapper
from scrapping.utils.utils import get_currency_value


class EtherScanScrapper(ScanScrapper):
    def __init__(self) -> None:
        super().__init__()
        self._base_url = 'https://etherscan.io/'

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
            action = Action.BUY.value if columns[4].text == Action.BUY else Action.SELL
            trades.append(TokenTrade(txn_hash=columns[1].text, action=action, amount_out=columns[5].text,
                                     amount_in=columns[6].text, value=get_currency_value(columns[8].text)))
        return trades
