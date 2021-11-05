from abc import ABC, abstractmethod


class ScanScrapper(ABC):
    @abstractmethod
    def get_trades(self, url: str):
        pass

    # save to es ?
    def save_trades(self):
        pass

    # send trades to kafka ?
    def send_trades(self):
        pass