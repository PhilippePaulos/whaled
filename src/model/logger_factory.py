import logging


class LoggerFactory:

    @staticmethod
    def __create_logger(log_file, level):
        logging.basicConfig(level=level)
        logger = logging.getLogger('logger')
        log_format = "%(asctime)s:%(levelname)s:%(message)s"
        formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.setLevel(level)
        file_handler.setLevel(level)
        stream_handler.setLevel(level)
        return logger

    @staticmethod
    def get_logger(log_file, log_level):
        return LoggerFactory.__create_logger(log_file, log_level)
