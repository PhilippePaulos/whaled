import logging
from decimal import Decimal
from re import sub

logger = logging.getLogger()


def get_currency_value(value: str) -> Decimal:
    return Decimal(sub(r'[^\d.]', '', value))
