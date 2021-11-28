import csv
import logging
import time
from abc import ABC, abstractmethod
from decimal import Decimal

from model.common.output import OutputFormats
from model.token_info import TokenInfo


class CurrencyScrapper(ABC):

    def __init__(self, token_adress: str, check_interval=0, output_format='', output_path='') -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress
        self.check_interval = check_interval
        self.output_format = output_format
        self.output_path = output_path

    def process(self) -> None:
        while True:
            token_info = self.get_token_info()
            self.save(token_info)
            self._logger.info(f'waiting (check interval={self.check_interval})...')
            time.sleep(self.check_interval)

    @abstractmethod
    def get_token_info(self) -> TokenInfo:
        pass

    @abstractmethod
    def get_currency_price(self) -> Decimal:
        pass

    @abstractmethod
    def get_currency_mcap(self) -> Decimal:
        pass

    @abstractmethod
    def get_token_url(self, token_adress: str) -> str:
        pass

    def save(self, token_info):
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            self.save_csv(self.output_path, token_info)
        else:
            raise NotImplemented(self.output_format)

    @staticmethod
    def save_csv(path: str, token_info: TokenInfo):
        with open(path, 'a') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([token_info.price, token_info.marketcap, token_info.datetime])
