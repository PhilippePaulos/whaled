from argparse import ArgumentParser

from model.common.logging import setup_log
from scrapping.currency_prices import settings
from scrapping.currency_prices.bogged_scrapper import BoggedScrapper
from scrapping.currency_prices.settings import load_settings


def run():
    args = parse_command_line()
    load_settings(args.config_path)
    setup_log(settings.logging_level, settings.logging_file)
    if settings.prices_blockchain.upper() in ['BSC', 'BINANCE']:
        print(BoggedScrapper().get_currency_price(settings.prices_token_adress))
    else:
        raise ValueError(f'Blockchain not supported: {settings.prices_blockchain}')


def parse_command_line():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_path', help='path to the job configuration', metavar='FILE')
    return parser.parse_args()


if __name__ == "__main__":
    run()
