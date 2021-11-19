import logging
from abc import ABC, abstractmethod


class CurrencyScrapper(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger()

    @abstractmethod
    def get_currency_price(self, token_adress: str):
        pass

    @abstractmethod
    def get_token_url(self, token_adress: str):
        pass
