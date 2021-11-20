import logging
import time
from abc import ABC, abstractmethod


class CurrencyScrapper(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger()

    def process(self, settings):
        while True:
            self.get_currency_price(settings.token_adress)
            self._logger.info(f'waiting (check interval={settings.check_interval})...')
            time.sleep(settings.check_interval)

    @abstractmethod
    def get_currency_price(self, token_adress: str):
        pass

    @abstractmethod
    def get_token_url(self, token_adress: str):
        pass
