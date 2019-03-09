import logging


class Log:
    LOGGER_NAME: str = 'sonoff-client'

    logger: logging.Logger = None

    @classmethod
    def init_log(cls) -> None:
        if cls.logger is None:
            cls.logger = logging.getLogger(cls.LOGGER_NAME)
            cls.logger.setLevel(logging.INFO)

            fh = logging.FileHandler('sonoff_client.log')

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            logger.addHandler(fh)
            logger.addHandler(ch)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return cls.logger

    @classmethod
    def debug(cls, message: str) -> None:
        cls.logger.debug(message)

    @classmethod
    def info(cls, message: str) -> None:
        cls.logger.info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        cls.logger.warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        cls.logger.error(message)


logger = logging.getLogger(Log.LOGGER_NAME)
logger.setLevel(logging.DEBUG)
Log.init_log()
