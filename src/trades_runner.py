from model.common.logging import setup_log
from model.common.utils import parse_command_line
from dex_trades.bsc_scrapper import BscScanScrapper
from dex_trades.ether_scrapper import EtherScanScrapper
from dex_trades.trades_config import TradesConfig


def run():
    args = parse_command_line()
    TradesConfig(args.config_path)
    setup_log(TradesConfig().logging_level, TradesConfig().logging_file)
    # TODO use factory pattern
    if TradesConfig().blockchain.upper() in ['BSC', 'BINANCE']:
        BscScanScrapper(TradesConfig().token_adress).process(TradesConfig().history)
    elif TradesConfig().blockchain.upper() in ['ETHER', 'ETH', 'ETHEREUM']:
        EtherScanScrapper(TradesConfig().token_adress).process(TradesConfig().history)
    else:
        raise ValueError(f'Could not identify blockchain type: {TradesConfig.blockchain}')


if __name__ == "__main__":
    run()
