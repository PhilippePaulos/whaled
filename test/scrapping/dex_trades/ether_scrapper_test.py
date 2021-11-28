import pathlib
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.ether_scrapper import EtherScanScrapper


class EtherScanScrapperTest(TestCase):

    @patch('scrapping.dex_trades.ether_scrapper.EtherScanScrapper.get_trades_url')
    def test_scrap(self, mock_get_trades_url):
        trades_html_path = pathlib.Path('resources/trades/etherscan/token_trades.html').resolve()
        mock_get_trades_url.return_value = f'file://{trades_html_path}'
        trades_list = EtherScanScrapper('0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3').get_trades()
        self.assertTrue(len(trades_list) == 25)
        self.assertTrue(
            trades_list[0] == TokenTrade(txn_hash='0x933fc590ed0538ffe8648a9aa0965b0e53cf33c8f4a802a6ee6aeb51d218a4f2',
                                         action=Action.BUY.value, amount=Decimal('5848500534.39251'),
                                         amount_in='5,848,500,534.39251 ELON',
                                         amount_out='2.23701713289359 ETH', value=Decimal('10047.61'))
        )
