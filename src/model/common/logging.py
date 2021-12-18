import logging


def setup_log(level_str, log_file=None):
    level = logging.getLevelName(level_str.upper())
    logging.getLogger('selenium').setLevel('INFO')
    logging.getLogger('webdriver_manager').setLevel('INFO')
    logging.getLogger('urllib3').setLevel('INFO')
    logger = logging.getLogger()
    logger.setLevel(level)
    log_format = "%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    logger.addHandler(stream_handler)
    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
