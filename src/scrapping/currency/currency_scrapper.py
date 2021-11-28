import logging
import time
import typing
from abc import abstractmethod
from decimal import Decimal

from model.common.output import OutputFormats
from model.common.writter import OutputWritter
from model.token_info import TokenInfo


class CurrencyScrapper(OutputWritter):

    def __init__(self, token_adress: str, check_interval=0, output_format='', output_path='') -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress
        self.check_interval = check_interval
        self.output_format = output_format
        self.output_path = output_path

    def process(self) -> None:
        while True:
            token_infos = [self.get_token_info()]
            self.save(token_infos)
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

    def save(self, token_infos: typing.List[TokenInfo]):
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            self.save_csv(self.output_path, token_infos)
        else:
            raise NotImplemented(self.output_format)
