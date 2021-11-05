import pathlib
from decimal import Decimal
from unittest import TestCase

from scrapping.ether_scrapper import EtherScanScrapper
from model.action import Action
from model.token_trade import TokenTrade


class ScrapperTest(TestCase):

    def test_scrap(self):
        trades_html_path = pathlib.Path('resources/trades/token_trades.html').resolve()
        trades_list = EtherScanScrapper().get_trades(f'file://{trades_html_path}')
        self.assertTrue(len(trades_list) == 25)
        self.assertTrue(
            trades_list[0] == TokenTrade(txn_hash='0x933fc590ed0538ffe8648a9aa0965b0e53cf33c8f4a802a6ee6aeb51d218a4f2',
                                               action=Action.SELL, amount_in='5,848,500,534.39251 ELON',
                                               amount_out='2.23701713289359 ETH',
                                               value=Decimal('10047.61'))
        )
