import pathlib
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from scrapping.currency_prices.bogged_scrapper import BoggedScrapper


class BoggedScrapperTest(TestCase):

    @patch('scrapping.currency_prices.bogged_scrapper.BoggedScrapper.get_token_url')
    def test_scrap(self, mock_get_token_url):
        token_html_path = pathlib.Path('resources/prices/bogged/bogged_token.html').resolve()
        mock_get_token_url.return_value = f'file://{token_html_path}'
        token_price = BoggedScrapper().get_currency_price('0x9D12CC56d133Fc5c60E9385B7A92F35a682da0bd')
        self.assertTrue(token_price == Decimal('0.0128340'))
