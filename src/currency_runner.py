from model.common.logging import setup_log
from model.common.utils import parse_command_line
from scrapping.currency import settings
from scrapping.currency.bogged_scrapper import BoggedScrapper
from scrapping.currency.settings import load_settings


def run():
    args = parse_command_line()
    load_settings(args.config_path)
    setup_log(settings.logging_level, settings.logging_file)
    # TODO use factory pattern
    if settings.blockchain.upper() in ['BSC', 'BINANCE']:
        BoggedScrapper(settings.token_adress, settings.check_interval, settings.output_format,
                       settings.output_path).process()
    else:
        raise ValueError(f'Blockchain not supported: {settings.blockchain}')


if __name__ == "__main__":
    run()
