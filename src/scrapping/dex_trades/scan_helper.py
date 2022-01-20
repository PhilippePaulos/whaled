import logging
import re
import typing
from decimal import Decimal, InvalidOperation

from model.action import Action
from model.token_trade import TokenTrade
from scrapping.utils.utils import get_currency_value, parse_time_ago


def get_trade_from_row(current_time, tr, token_adress, chain='bsc'):
    if chain == 'bsc':
        return get_trade_from_row_bsc(current_time, tr, token_adress)
    elif chain == 'ether':
        return get_trade_from_row_ether(tr, token_adress)
    else:
        raise NotImplementedError


def get_trade_from_row_bsc(current_time, tr, token_adress):
    columns = tr.xpath(".//td")
    txn_hash = columns[0].xpath('string()').get()
    maker_adress = columns[2].xpath('.//a/@href').get().split('/')[-1]
    taker_adress = columns[4].xpath('.//a/@href').get().split('/')[-1]
    amount_out = columns[2].xpath('./text()').get().strip()
    token_out = columns[2].xpath('./a/text()').get().strip()
    amount_in = columns[4].xpath('./text()').get().strip()
    token_in = columns[4].xpath('./a/text()').get().strip()
    action, amount = get_amount_action(maker_adress, taker_adress, token_adress, amount_out, amount_in)
    time_ago_str = columns[1].xpath('.//text()').get()
    trade_date = parse_time_ago(current_time, time_ago_str)

    return TokenTrade(txn_hash=txn_hash, action=action, amount=amount,
                      amount_out=f'{amount_out} {token_out}', amount_in=f'{amount_in} {token_in}',
                      timestamp=trade_date)


def get_trade_from_row_ether(tr, token_adress):
    columns = tr.xpath(".//td")
    txn_hash = columns[1].xpath('string()').get()
    amount_out = columns[5].xpath('text()').get().strip()
    amount_in = columns[6].xpath('text()').get().strip()
    if 'ETH' in amount_in:
        amount_in = re.sub(r'ETH$', '', amount_in).strip()
        token_in = 'ETH'
        taker_adress = None
    else:
        token_in = columns[6].xpath('./a/text()').get()
        taker_adress = columns[6].xpath('.//a/@href').get().split('/')[-1]
    if 'ETH' in amount_out:
        amount_out = re.sub(r'ETH$', '', amount_out).strip()
        token_out = 'ETH'
        maker_adress = None
    else:
        token_out = columns[5].xpath('./a/text()').get()
        maker_adress = columns[5].xpath('.//a/@href').get().split('/')[-1]

    action_str = columns[4].xpath('string()').get().upper()

    if action_str == Action.BUY.name:
        action = Action.BUY.value
        amount = get_currency_value(amount_in)
    elif action_str == Action.SELL.name:
        action = Action.SELL.value
        amount = get_currency_value(amount_out)
    elif action_str == Action.SWAP.name:
        action, amount = get_amount_action(maker_adress, taker_adress, token_adress, amount_out, amount_in)
    else:
        logging.warning('Could not get action type')
        action = Action.UNKNOWN.value
        amount = Decimal('0')
    txn_value = -1
    try:
        txn_value = get_currency_value(columns[8].xpath('string()').get())
    except InvalidOperation:
        # TODO GET VALUE FROM THE TXN
        logging.error(f"Could not convert to decimal value: {columns[8].xpath('string()').get()}")

    time = columns[2].xpath('string()').get()

    return TokenTrade(txn_hash=txn_hash, action=action, amount=amount, amount_out=f'{amount_out} {token_out}',
                      amount_in=f'{amount_in} {token_in}', timestamp=time, value=txn_value)


def get_amount_action(maker_adress, taker_adress, token_adress, amount_out, amount_in) -> typing.Tuple[Action, Decimal]:
    amount = Decimal('0')
    if maker_adress.upper() == token_adress.upper():
        action = Action.SELL.value
        amount = Decimal(get_currency_value(amount_out))
    elif taker_adress.upper() == token_adress.upper():
        action = Action.BUY.value
        amount = Decimal(get_currency_value(amount_in))
    else:
        logging.warning('Could not get action type')
        action = Action.UNKNOWN.value
    return action, amount
