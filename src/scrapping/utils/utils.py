from decimal import Decimal
from re import sub


def get_currency_value(value: str) -> Decimal:
    return Decimal(sub(r'[^\d.]', '', value))
