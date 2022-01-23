from dex_trades.history_scraper import EtherHistoryScraper
from dex_trades.trades_scrapper import ScanScrapper


class EtherScanScrapper(ScanScrapper):

    def __init__(self, token_adress:str) -> None:
        super().__init__(token_adress)

    @property
    def base_url(self) -> str:
        return 'https://etherscan.io/'

    @property
    def history_module(self):
        return EtherHistoryScraper

    def get_trades_url(self) -> str:
        return f'{self.base_url}dextracker_txns?q={self.token_adress}&p=1&ps=100'

    @property
    def tr_xpath(self):
        return "//*[@id='doneloadingframe']//tbody/tr"
