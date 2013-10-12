#coding: utf-8

from flask import Flask


def build(**settings):
    app = Flask(__name__)

    app.config.from_envvar('LIB_READER_CONFIG', silent=True)
    app.config.update(settings)

    register_blueprint(app)
    # register_logging(app)

    return app


def register_blueprint(app):
    from .views import user
    app.register_blueprint(user.app, url_prefix='/user')

    return app


def register_logging(app):
    import logging.config

    logging.config.dictConfig(app.config['LOGGING_CONFIG'])

    return app
