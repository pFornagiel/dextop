# Utils
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

MAX_BYTES = 5_000_000

class Logger:
  _instance = None

  def __new__(cls, path: str, logger_name: str):
    if(cls._instance is None):
      cls._instance = super(Logger, cls).__new__(cls)
      cls._instance._initialise(path, logger_name)
    return cls._instance
  
  def _initialise(self, path: str, logger_name: str) -> None:
    self._PATH = path
    os.makedirs(self._PATH, exist_ok=True)
    self._logger = self._setup_logger(logger_name)
  
  def _setup_logger(self, logger_name: str) -> logging.Logger:
    now = datetime.now()
    month = now.strftime('%m')
    year = now.strftime('%Y')
    log_filename = os.path.join(self._PATH, f'{month}-{year}-log.txt')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    if(not logger.hasHandlers()):
      handler = RotatingFileHandler(log_filename, maxBytes=MAX_BYTES)  # 5MB per log
      formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M %d-%m-%Y')
      handler.setFormatter(formatter)
      logger.addHandler(handler)

    return logger
  
  def add_entry(self, entry: str, level: str = 'INFO') -> None:
    match level.upper():
      case 'DEBUG':
        self._logger.debug(entry)
      case 'WARNING':
        self._logger.warning(entry)
      case 'ERROR':
        self._logger.error(entry)
      case 'CRITICAL':
        self._logger.critical(entry)
      case _:
        self._logger.info(entry)
