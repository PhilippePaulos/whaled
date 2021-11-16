import logging
from datetime import timedelta
from decimal import Decimal
from re import sub
from timeit import default_timer


from model.logger_factory import LoggerFactory


def get_currency_value(value: str) -> Decimal:
    return Decimal(sub(r'[^\d.]', '', value))


def processing_time():
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = LoggerFactory().get_logger(logging.INFO, log_file='bsc_scrapper.log')
            before = default_timer()
            result = func(*args, **kwargs)
            after = default_timer()
            if logger.level == logging.DEBUG:
                logger.debug(f'Process time is: {timedelta(seconds=after - before)}')
            return result

        return wrapper

    return decorator
