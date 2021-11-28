import logging
import typing
from abc import ABC, abstractmethod

from model.common.utils import processing_time
from model.token_trade import TokenTrade


class ScanScrapper(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger()

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    def process(self, settings):
        print(self.get_trades(settings.token_adress))

    @abstractmethod
    @processing_time()
    def get_trades(self, token_adress: str) -> typing.List[TokenTrade]:
        pass

    def get_trades_url(self, token_adress: str) -> str:
        return f'{self.base_url}/token/{token_adress}#tokenTrade'

    # save to es ?
    def save_trades(self):
        pass
