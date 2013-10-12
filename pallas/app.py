#coding: utf-8

from flask import Flask


def build(**settings):
    app = Flask(__name__)

    app.config.from_envvar('LIB_READER_CONFIG', silent=True)
    app.config.update(settings)

    return app


def register_blueprint(app):
    return app


def register_logging(app):
    import logging.config

    logging.config.dictConfig(app.config['LOGGING_CONFIG'])

    return app
