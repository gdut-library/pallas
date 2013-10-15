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
        'app.log': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.abspath('logs/app.debug.log'),
            'formatter': 'brief'
        },
        'tasks.log': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.abspath('logs/tasks.debug.log'),
            'formatter': 'brief'
        }
    },
    'loggers': {
        'app': {
            'propagate': True,
            'level': 'DEBUG',
            'handlers': ['console', 'app.log']
        },
        'tasks': {
            'propagate': True,
            'level': 'DEBUG',
            'handlers': ['console', 'tasks.log']
        }
    },
    'disable_existing_loggers': True,
    'incremental': False,
    'version': 1
}

TASKS = {
    'user': {
        'update_interval': 120
    }
}
