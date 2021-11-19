from datetime import datetime
from decimal import Decimal


class TokenPrice:
    def __init__(self, price: Decimal, date: datetime) -> None:
        super().__init__()
        self.price = price
        self.datetime = date

    def __str__(self) -> str:
        return f'price: {self.price}$ at {self.datetime}'
