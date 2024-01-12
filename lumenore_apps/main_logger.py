import sys
import logging
import logging.config
from .constants import Constants

constants = Constants()

FORMATTER = logging.Formatter(f"[{constants.get_config('parameters', 'env')}] "
                              f"[%(levelname)s]: [%(asctime)s] [%(lineno)d] [%(filename)s] [%(message)s]")


def get_console_handler():
    """update this doc string"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(logging.INFO)
    return console_handler


def set_up_logging():
    """Set up logging"""
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        logger.addHandler(get_console_handler())
        logger.propagate = False
    return logger