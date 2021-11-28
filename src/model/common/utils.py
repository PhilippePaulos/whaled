import csv
import logging
import typing
from argparse import ArgumentParser
from datetime import timedelta
from timeit import default_timer

logger = logging.getLogger()


def processing_time():
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logger.level == logging.DEBUG:
                before = default_timer()
                result = func(*args, **kwargs)
                after = default_timer()
                logger.debug(f'Process time is: {timedelta(seconds=after - before)}')
            else:
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def parse_command_line():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_path', help='path to the job configuration', metavar='FILE')
    return parser.parse_args()


def export_objects_to_csv(path: str, instance_list: typing.List[object], mode='a', delimiter=';'):
    with open(path, mode) as f:
        writer = csv.writer(f, delimiter=delimiter)
        rows = []
        for instance in instance_list:
            object_dict = instance.__dict__
            values = [object_dict[attr] for attr in object_dict]
            rows.append(values)
        writer.writerows(rows)
