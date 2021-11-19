from argparse import ArgumentParser

from scrapping.dex_trades import settings
from model.common.logging import setup_log

from scrapping.dex_trades.bsc_scrapper import BscScanScrapper
from scrapping.dex_trades.ether_scrapper import EtherScanScrapper
from scrapping.dex_trades.settings import load_settings


def run():
    args = parse_command_line()
    load_settings(args.config_path)
    setup_log(settings.logging_level, settings.logging_file)
    if settings.blockchain.upper() in ['BSC', 'BINANCE']:
        print(BscScanScrapper().get_trades(settings.token_adress))
    elif settings.blockchain.upper() in ['ETHER', 'ETH', 'ETHERUM']:
        print(EtherScanScrapper().get_trades(settings.token_adress))
    else:
        raise ValueError(f'Could not identify blockchain type: {settings.blockchain}')


def parse_command_line():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_path', help='path to the job configuration', metavar='FILE')
    return parser.parse_args()


if __name__ == "__main__":
    run()
