from model.common.logging import setup_log
from model.common.utils import parse_command_line
from scrapping.dex_trades import settings
from scrapping.dex_trades.bsc_scrapper import BscScanScrapper
from scrapping.dex_trades.ether_scrapper import EtherScanScrapper
from scrapping.dex_trades.settings import load_settings


def run():
    args = parse_command_line()
    load_settings(args.config_path)
    setup_log(settings.logging_level, settings.logging_file)
    # TODO use factory pattern
    if settings.blockchain.upper() in ['BSC', 'BINANCE']:
        BscScanScrapper(settings.token_adress, settings.output_format, settings.output_path).process()
    elif settings.blockchain.upper() in ['ETHER', 'ETH', 'ETHEREUM']:
        EtherScanScrapper(settings.token_adress, settings.output_format, settings.output_path).process()
    else:
        raise ValueError(f'Could not identify blockchain type: {settings.blockchain}')


if __name__ == "__main__":
    run()
