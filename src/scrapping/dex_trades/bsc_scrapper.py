from scrapping.currency.bogged_scrapper import BoggedScrapper
from scrapping.dex_trades.history_scraper import BscHistoryScraper
from scrapping.dex_trades.trades_scrapper import ScanScrapper


class BscScanScrapper(ScanScrapper):

    def __init__(self, token_adress: str) -> None:
        super().__init__(token_adress)

    @property
    def base_url(self) -> str:
        return 'https://bscscan.com'

    @property
    def history_module(self):
        return BscHistoryScraper

    def get_trades_url(self) -> str:
        return f'{self.base_url}/dextracker?q={self.token_adress}&ps={self.MAX_NUM_TRADES}'

    @property
    def tr_xpath(self):
        return "//main[@id='content']//div[contains(@class, 'card')]//tbody/tr"

    def get_token_info(self):
        return BoggedScrapper(self.token_adress, load_marketcap=False).get_token_info(self.token_adress,
                                                                                      load_marketcap=False)
