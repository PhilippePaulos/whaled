import logging
import typing
from abc import ABC, abstractmethod

from model.common.logger_factory import LoggerFactory
from model.token_trade import TokenTrade
from scrapping.utils.utils import processing_time


class ScanScrapper(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger()

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    @processing_time()
    def get_trades(self, token_adress: str) -> typing.List[TokenTrade]:
        pass

    def get_trades_url(self, token_adress: str) -> str:
        return f'{self.base_url}/token/{token_adress}#tokenTrade'

    # save to es ?
    def save_trades(self):
        pass

    # send trades to kafka ?
    def send_trades(self):
        pass