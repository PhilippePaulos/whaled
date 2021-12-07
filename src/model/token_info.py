from datetime import datetime
from decimal import Decimal
from typing import Optional


class TokenInfo:
    def __init__(self, price: Decimal, marketcap: Optional[Decimal], date: datetime) -> None:
        super().__init__()
        self.price = price
        self.marketcap = marketcap
        self.datetime = date

    def __str__(self) -> str:
        return f'price: {self.price}$, marketcap: {self.marketcap}$, time: {self.datetime}'
