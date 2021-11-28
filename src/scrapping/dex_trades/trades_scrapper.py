import logging
import typing
from abc import abstractmethod

from model.common.output import OutputFormats
from model.common.utils import processing_time
from model.token_trade import TokenTrade
from scrapping.currency.currency_scrapper import OutputWritter


class ScanScrapper(OutputWritter):

    def __init__(self, token_adress: str, output_format=None, output_path=None) -> None:
        super().__init__()
        self._logger = logging.getLogger()
        self.token_adress = token_adress
        self.output_format = output_format
        self.output_path = output_path

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    def process(self):
        trades = self.get_trades()
        self.save(trades)

    @abstractmethod
    @processing_time()
    def get_trades(self) -> typing.List[TokenTrade]:
        pass

    def get_trades_url(self, token_adress: str) -> str:
        return f'{self.base_url}/token/{token_adress}#tokenTrade'

    def save(self, trades):
        if self.output_format.upper() == OutputFormats.OUTPUT_CSV:
            self.save_csv(self.output_path, trades)
        else:
            raise NotImplemented(self.output_format)
