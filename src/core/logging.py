from logging import DEBUG, INFO, WARNING, Formatter, Logger, StreamHandler, basicConfig, getLogger, info

from config.settings import Settings

DEFAULT_LOGGER_NAME = 'bot'
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(filename)s(line %(lineno)d) - %(funcName)s - %(message)s'


def init_logger() -> None:
    bot_logger = getLogger(name=DEFAULT_LOGGER_NAME)
    bot_formatter = Formatter(fmt=LOG_FORMAT)
    bot_stream_handler = StreamHandler()

    bot_stream_handler.setFormatter(fmt=bot_formatter)
    bot_stream_handler.setLevel(level=DEBUG)

    bot_logger.addHandler(bot_stream_handler)

    if Settings().app.debug:
        bot_logger.setLevel(level=DEBUG)
    else:
        bot_logger.setLevel(level=INFO)
    bot_logger.debug("bot logger initialized")
    pass


def log() -> Logger:
    return getLogger(name=DEFAULT_LOGGER_NAME)
