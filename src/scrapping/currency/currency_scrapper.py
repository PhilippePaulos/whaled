import logging
import time
from abc import ABC, abstractmethod

from model.token_info import TokenInfo


class CurrencyScrapper(ABC):

    def __init__(self, token_adress) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress

    def process(self, check_interval):
        while True:
            self.get_token_info()
            self._logger.info(f'waiting (check interval={check_interval})...')
            time.sleep(check_interval)

    @abstractmethod
    def get_token_info(self) -> TokenInfo:
        pass

    @abstractmethod
    def get_currency_price(self):
        pass

    @abstractmethod
    def get_currency_mcap(self):
        pass

    @abstractmethod
    def get_token_url(self, token_adress: str):
        pass
