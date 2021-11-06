from abc import ABC, abstractmethod


class CurrencyScrapper(ABC):

    @abstractmethod
    def get_currency_price(self, token_adress: str):
        pass

    @abstractmethod
    def get_token_url(self, token_adress: str):
        pass
