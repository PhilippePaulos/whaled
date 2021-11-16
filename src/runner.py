import logging

from model.common import settings
from model.common.logging import setup_log
from model.common.settings import load_settings
from scrapping.dex_trades.bsc_scrapper import BscScanScrapper
from scrapping.dex_trades.ether_scrapper import EtherScanScrapper


def run():
    load_settings()
    setup_log(settings.logging_level, settings.logging_file)
    log = logging.getLogger()
    if settings.trades_blockchain.upper() in ['BSC', 'BINANCE']:
        print(BscScanScrapper().get_trades(settings.trades_token_adress))
    elif settings.trades_blockchain.upper() in ['ETHER', 'ETH', 'ETHERUM']:
        print(EtherScanScrapper().get_trades(settings.trades_token_adress))
    else:
        raise ValueError(f'Could not identify blockchain type: {settings.trades_blockchain}')


if __name__ == "__main__":
    run()
