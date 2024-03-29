import logging
import os.path
import time
import typing
from abc import abstractmethod
from decimal import Decimal

from model.common.output import OutputFormats
from model.common.writter import OutputWritter
from model.token_info import TokenInfo
from currency.currency_config import CurrencyConfig


class CurrencyScrapper(OutputWritter):

    def __init__(self, token_adress: str) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self._token_adress = token_adress
        self.check_interval = CurrencyConfig().check_interval
        self.output_format = CurrencyConfig().output_format
        self.output_path = CurrencyConfig().output_path

    @property
    def token_adress(self):
        return self._token_adress

    @token_adress.setter
    def token_adress(self, value):
        self._token_adress = value

    def process(self) -> None:
        while True:
            token_infos = [self.get_token_info(self.token_adress)]
            self.save(token_infos)
            self._logger.info(f'waiting (check interval={self.check_interval})...')
            time.sleep(self.check_interval)

    @abstractmethod
    def get_token_info(self, token_adress, load_marketcap=True) -> TokenInfo:
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

    def save(self, token_infos: typing.List[TokenInfo]):
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            self.save_csv(os.path.join(self.output_path, f'token_info_{self.token_adress}.csv'), token_infos)
        elif self.output_format.upper() == OutputFormats.OUTPUT_ES:
            self.save_es(f'token_{self.token_adress}', token_infos, CurrencyConfig().es_host, CurrencyConfig().es_port)
        else:
            raise NotImplemented(self.output_format)
