import logging
import os
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Union

log = logging.getLogger(__name__)

_log_format = '%(asctime)s.%(msecs)03d [%(module)7s] [%(levelname)5s] %(message)s'
_date_format = '%H:%M:%S'

_log_dir = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'log')


class SimpleLogger(object):
    def __init__(self, logger=None, level=logging.INFO, file_name=None, log_dir=_log_dir, fmt=_log_format,
                 datefmt=_date_format, backup_count=1, max_bytes=(1024 * 1024)):
        self.handler = None  # type: Union[StreamHandler, RotatingFileHandler]
        self.formatter = None  # type: logging.Formatter
        self.path = None  # type: str
        self.level = level  # type: int
        self.logger = None  # type: SimpleLogger

        if file_name is None:
            self.handler = logging.StreamHandler()
        else:
            self.path = os.path.join(log_dir, file_name + '.log')
            if not os.path.isdir(log_dir):
                raise NotADirectoryError('\'\\log\' directory doesn\'t exist in the current working directory.')
            self.handler = RotatingFileHandler(self.path, 'a', max_bytes, backup_count, 'utf-8')

        self.formatter = logging.Formatter(fmt, datefmt)
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(self.level)

        if logger is not None:
            self.attach_to(logger)

    def attach_to(self, logger):
        if isinstance(logger, str):
            logger = logging.getLogger(logger)
        self.logger = logger
        self.logger.addHandler(self.handler)
