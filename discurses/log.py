import logging
import logging.config
import os
import sys

LOG_FILE_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "discurses.log")

# Empty the log
open(LOG_FILE_PATH, 'w').close()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
    },
    'handlers': {
        "default": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": LOG_FILE_PATH,
            "maxBytes": 10485760,
            "backupCount": 2,
            "encoding": "utf8"
        },
    },
    'loggers': {
        'discord': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'discurses': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"]
    }
})

# Install exception handler
logger = logging.getLogger('discurses')
logger.info("Now logging!")
