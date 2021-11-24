import pathlib
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from scrapping.currency.bogged_scrapper import BoggedScrapper


class BoggedScrapperTest(TestCase):

    @patch('scrapping.currency.bogged_scrapper.BoggedScrapper.get_token_url')
    def test_scrap(self, mock_get_token_url):
        token_html_path = pathlib.Path('resources/prices/bogged/bogged_token.html').resolve()
        mock_get_token_url.return_value = f'file://{token_html_path}'
        token_info = BoggedScrapper('0x2859e4544c4bb03966803b044a93563bd2d0dd4d').get_token_info()
        self.assertTrue(token_info.price == Decimal('0.0000485309'))
        self.assertTrue(token_info.marketcap == Decimal('209640000'))
