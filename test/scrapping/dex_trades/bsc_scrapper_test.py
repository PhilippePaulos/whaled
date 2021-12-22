import csv
import os
import pathlib
import tempfile
from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from model.action import Action
from model.token_info import TokenInfo
from model.token_trade import TokenTrade
from scrapping.dex_trades.bsc_scrapper import BscScanScrapper


class BscScanScrapperTest(TestCase):

    @patch('scrapping.dex_trades.bsc_scrapper.BscScanScrapper.get_trades_url')
    @patch('scrapping.currency.bogged_scrapper.BoggedScrapper.get_token_info')
    def test_scrap(self, mock_get_token_info, mock_get_trades_url):
        token_html_path = pathlib.Path('resources/prices/bogged/bogged_token.html').resolve()
        mock_get_token_info.return_value = TokenInfo(Decimal('1'), None, datetime.now())
        trades_html_path = pathlib.Path('resources/trades/bscscan/token_trades.html').resolve()
        mock_get_trades_url.return_value = f'file://{trades_html_path}'

        trades_list = BscScanScrapper('0x2859e4544c4bb03966803b044a93563bd2d0dd4d').get_trades_with_price(Decimal('1'))[0]
        self.assertTrue(len(trades_list) == 25)
        self.assertTrue(
            trades_list[0] == TokenTrade(txn_hash='0x0ff34dfc1c96a93d6c535d9bd8fb7658ca377d9868017859163d33da7286d1d9',
                                         action=Action.SELL.value, amount=Decimal('25080882.4388396'),
                                         amount_in='1,068.91875726039 BSC-USD', amount_out='25,080,882.4388396 SHIB',
                                         timestamp=datetime.now(), value=Decimal('25080882.4388396'))
        )
        self.assertTrue(
            trades_list[-1] == TokenTrade(txn_hash='0x3a5ca74140711aefb3a8c712e901f92b355b16694ab17958b8fb39154b8dec4d',
                                          action=Action.BUY.value, amount=Decimal('23507801.506527'),
                                          amount_in='23,507,801.506527 SHIB', amount_out='1.61455797768236 WBNB',
                                          timestamp=datetime.now(), value=Decimal('23507801.506527'))
        )

    def test_save_csv(self):
        token_trade = TokenTrade(txn_hash='0xa0ec390af06c29592d1d776fd2e3f954a69801aa55b735a59cfafa73fcac47bd',
                                 action=Action.BUY.value, amount=Decimal('535664.913904223'),
                                 amount_in='535664.913904223 SHIB', amount_out='0.0555153483551779 WBNB',
                                 timestamp=datetime.now(), value=Decimal('25.9963003701944559907'))

        with tempfile.TemporaryDirectory() as d:
            output_path = os.path.join(d, 'outputs')
            BscScanScrapper.save_csv(output_path, [token_trade])
            with open(output_path, 'r') as output_file:
                reader = csv.reader(output_file, delimiter=';')
                row = reader.__next__()
                self.assertTrue(TokenTrade(row[0], int(row[1]), Decimal(row[2]), row[3], row[4], str(row[5]),
                                           Decimal(row[6])) == token_trade)
