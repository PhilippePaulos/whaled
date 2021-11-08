from abc import ABC, abstractmethod


class ScanScrapper(ABC):

    @property
    @abstractmethod
    def base_url(self):
        pass

    @abstractmethod
    def get_trades(self, token_adress: str):
        pass

    def get_trades_url(self, token_adress: str):
        return f'{self.base_url}/token/{token_adress}#tokenTrade'

    # save to es ?
    def save_trades(self):
        pass

    # send trades to kafka ?
    def send_trades(self):
        pass