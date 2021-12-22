from decimal import Decimal


class TokenTrade:

    def __init__(self, txn_hash: str, action: int, amount: Decimal, amount_out: str, amount_in: str, timestamp,
                 value: Decimal = Decimal('0')) -> None:
        self.txn_hash = txn_hash
        self.action = action
        self.amount = amount
        self.amount_out = amount_out
        self.amount_in = amount_in
        self.timestamp = timestamp
        self.value = value

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TokenTrade):
            return self.txn_hash == o.txn_hash and self.action == o.action and self.amount == o.amount and \
                   self.amount_out == o.amount_out and self.amount_in == o.amount_in
        return False

    def __str__(self) -> str:
        return f'txn_hash: {self.txn_hash}, action: {self.action}, amount: {self.amount}, ' \
               f'amount_out: {self.amount_out}, amount_in: {self.amount_in}, value: {self.value},' \
               f' timestamp: {self.timestamp}'
