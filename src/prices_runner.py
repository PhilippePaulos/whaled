import logging
from argparse import ArgumentParser

from model.common.logging import setup_log
from model.common.utils import parse_command_line
from scrapping.currency_prices import settings
from scrapping.currency_prices.bogged_scrapper import BoggedScrapper
from scrapping.currency_prices.settings import load_settings


def run():
    args = parse_command_line()
    load_settings(args.config_path)
    setup_log(settings.logging_level, settings.logging_file)
    # TODO use factory pattern
    if settings.blockchain.upper() in ['BSC', 'BINANCE']:
        BoggedScrapper().process(settings)
    else:
        raise ValueError(f'Blockchain not supported: {settings.blockchain}')


if __name__ == "__main__":
    run()
