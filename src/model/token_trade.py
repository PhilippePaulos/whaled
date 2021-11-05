from decimal import Decimal

from model.action import Action


class TokenTrade:

    def __init__(self, txn_hash: str, action: Action, amount_out: str, amount_in: str, value: Decimal) -> None:
        self.txn_hash = txn_hash
        self.action = action
        self.amount_out = amount_out
        self.amount_in = amount_in
        self.value = value

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TokenTrade):
            return self.txn_hash == o.txn_hash and self.action == o.action and self.amount_out == o.amount_out \
                   and self.amount_in == o.amount_in
        return False
