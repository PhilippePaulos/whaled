import logging
import random
import re
from datetime import timedelta
from decimal import Decimal
from re import sub

from constants.web import USER_AGENT_LIST

logger = logging.getLogger()


def get_currency_value(value: str) -> Decimal:
    return Decimal(sub(r'[^\d.]', '', value))


def parse_time_ago(current_time, time_ago_str):
    def compute_delta(computed_time, time_str, digit, delta_type, check_day=True):
        if delta_type in 'sec':
            return computed_time - timedelta(seconds=digit)
        if delta_type in 'min':
            return computed_time - timedelta(minutes=digit)
        elif delta_type in 'hr':
            return computed_time - timedelta(hours=digit)
        elif delta_type in 'day' and check_day:
            return computed_time - timedelta(days=digit)
        else:
            logging.error(f'Could not parse {time_str} correctly')
            return computed_time

    match = re.match(r"(^\d*) (sec|day|hr|min).? ago$", time_ago_str)
    if match:
        return compute_delta(current_time, time_ago_str, int(match.group(1)), match.group(2))
    else:
        match = re.match(r"(^\d*) (sec|day|hr|min).? (\d*) (sec|hr|min).? ago$", time_ago_str)
        if match:
            delta_time = compute_delta(current_time, time_ago_str, int(match.group(1)), match.group(2))
            return compute_delta(delta_time, time_ago_str, int(match.group(3)), match.group(4), check_day=False)
        else:
            logging.error(f"Could not parse {time_ago_str} correctly. This pattern doesn't match any regex")


def get_headers():
    user_agent = USER_AGENT_LIST[random.randint(0, len(USER_AGENT_LIST) - 1)]
    return {'User-Agent': user_agent}
