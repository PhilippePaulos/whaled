import csv
import os
import pathlib
import tempfile
from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from model.token_info import TokenInfo
from scrapping.currency.bogged_scrapper import BoggedScrapper


class BoggedScrapperTest(TestCase):

    @patch('scrapping.currency.bogged_scrapper.BoggedScrapper.get_token_url')
    def test_get_token_info(self, mock_get_token_url):
        token_html_path = pathlib.Path('resources/prices/bogged/bogged_token.html').resolve()
        mock_get_token_url.return_value = f'file://{token_html_path}'
        token_info = BoggedScrapper('0x2859e4544c4bb03966803b044a93563bd2d0dd4d', 0, '', '')\
            .get_token_info('0x2859e4544c4bb03966803b044a93563bd2d0dd4d')
        self.assertTrue(token_info.price == Decimal('0.0000485309'))
        self.assertTrue(token_info.marketcap == Decimal('209640000'))

    def test_save_csv(self):
        now = datetime.now()
        token_info = TokenInfo(Decimal('1'), Decimal('2'), now)

        with tempfile.TemporaryDirectory() as d:
            output_path = os.path.join(d, 'outputs')
            BoggedScrapper.save_csv(output_path, [token_info])
            with open(output_path, 'r') as output_file:
                reader = csv.reader(output_file, delimiter=';')
                row = reader.__next__()
                self.assertTrue(TokenInfo(Decimal(row[0]), Decimal(row[1]),
                                          datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f')), token_info)
