import logging
import time


class ColorCodes:
    USE_COLOR = True
    RESET_SEQ = '\x1b[0m'
    GREY = '\x1b[0;37;20m'
    GREEN = '\x1b[1;32m'
    YELLOW = '\x1b[33;20m'
    RED = '\x1b[31;20m'
    BOLD_RED = '\x1b[31;1m'
    BLUE = '\x1b[1;34m'
    LIGHT_BLUE = '\x1b[1;36m'
    PURPLE = '\x1b[1;35m'
    WHITE = '\x1b[37m'
    COLORS = {
        'CRITICAL': BOLD_RED,
        'ERROR': RED,
        'WARNING': YELLOW,
        'INFO': GREEN,
        'DEBUG': BLUE,
    }


class CustomFormatter(logging.Formatter):
    tz = time.strftime('%Z')
    FORMAT = (
        f'%(asctime)s.%(msecs)03d {tz} : %(levelname)s : %(name)s [%(funcName)s] : '
    )
    MESSAGE = '%(message)s'

    def __init__(self, use_color: bool = ColorCodes.USE_COLOR) -> None:
        super().__init__()
        if use_color:
            self.fmt = {
                level: color + self.FORMAT + ColorCodes.WHITE + self.MESSAGE + ColorCodes.RESET_SEQ
                for level, color in ColorCodes.COLORS.items()
            }
        else:
            self.fmt = {
                level: self.FORMAT + self.MESSAGE
                for level, color in ColorCodes.COLORS.items()
            }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.fmt.get(record.levelname, self.FORMAT + self.MESSAGE)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class CustomLogger(logging.StreamHandler):
    def __init__(self) -> None:
        super().__init__()

        logging.logProcesses = False
        logging.logThreads = False
        logging.logMultiprocessing = False

        self.setFormatter(CustomFormatter())


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(CustomLogger())
    return logger
