import logging


class LoggerFactory:

    logger = None

    @staticmethod
    def __create_logger(level, log_file=None):
        logging.basicConfig(level=level)
        logger = logging.getLogger('logger')
        logger.setLevel(level)
        log_format = "%(asctime)s:%(levelname)s:%(message)s"
        formatter = logging.Formatter(log_format)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        if log_file is not None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)
        LoggerFactory.logger = logger
        return LoggerFactory.logger

    @staticmethod
    def get_logger(log_level, log_file=None):
        if LoggerFactory.logger is not None:
            return LoggerFactory.logger
        else:
            return LoggerFactory.__create_logger(log_level, log_file=log_file)
