from model.common.logging import setup_log
from model.common.utils import parse_command_line
from currency.bogged_scrapper import BoggedScrapper
from currency.currency_config import CurrencyConfig


def run():
    args = parse_command_line()
    CurrencyConfig(args.config_path)
    setup_log(CurrencyConfig().logging_level, CurrencyConfig().logging_file)
    # TODO use factory pattern
    if CurrencyConfig().blockchain.upper() in ['BSC', 'BINANCE']:
        BoggedScrapper(CurrencyConfig().token_adress, CurrencyConfig().check_interval).process()
    else:
        raise ValueError(f'Blockchain not supported: {CurrencyConfig().blockchain}')


if __name__ == "__main__":
    run()
