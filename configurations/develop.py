#coding: utf-8

import os

DEBUG = True

SECRET_KEY = 'reader digest'

LOGGING_CONFIG = {
    'formatters': {
        'brief': {
            'format': '%(levelname)s %(name)s %(message)s'
        }
    },
    'filters': [],
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief'
        },
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.abspath('logs/app.debug.log'),
            'formatter': 'brief'
        }
    },
    'loggers': {
        'app': {
            'propagate': True,
            'level': 'DEBUG',
            'handlers': ['console', 'logfile']
        }
    },
    'disable_existing_loggers': True,
    'incremental': False,
    'version': 1
}
