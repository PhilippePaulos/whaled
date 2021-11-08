from datetime import datetime
from decimal import Decimal


class TokenPrice:
    def __init__(self, price: Decimal, date: datetime) -> None:
        super().__init__()
        self.price = price
        self.datetime = datetime
