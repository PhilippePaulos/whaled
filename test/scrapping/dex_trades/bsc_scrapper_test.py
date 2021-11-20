import pathlib
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.dex_trades.bsc_scrapper import BscScanScrapper


class BscScanScrapperTest(TestCase):

    @patch('scrapping.dex_trades.bsc_scrapper.BscScanScrapper.get_trades_url')
    def test_scrap(self, mock_get_trades_url):
        trades_html_path = pathlib.Path('resources/trades/bscscan/token_trades.html').resolve()
        mock_get_trades_url.return_value = f'file://{trades_html_path}'
        trades_list = BscScanScrapper().get_trades('0x2859e4544c4bb03966803b044a93563bd2d0dd4d')
        self.assertTrue(len(trades_list) == 25)
        self.assertTrue(
            trades_list[0] == TokenTrade(txn_hash='0xa0ec390af06c29592d1d776fd2e3f954a69801aa55b735a59cfafa73fcac47bd',
                                         action=Action.BUY.value, amount=Decimal('535664.913904223'),
                                         amount_in='535664.913904223 SHIB', amount_out='0.0555153483551779 WBNB',
                                         value=Decimal('25.9694099915164639961'))
        )
