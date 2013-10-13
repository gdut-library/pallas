#coding: utf-8

from flask import Flask


def build(**settings):
    app = Flask(__name__.replace('.', '-'))

    app.config.from_envvar('LIB_READER_CONFIG', silent=True)
    app.config.update(settings)

    register_mongo(app)
    register_rq(app)
    register_blueprint(app)
    register_logging(app)

    return app


def register_blueprint(app):
    from .views import user
    app.register_blueprint(user.app, url_prefix='/user')

    return app


def register_logging(app):
    import logging.config

    logging.config.dictConfig(app.config['LOGGING_CONFIG'])

    return app


def register_mongo(app):
    from flask.ext.pymongo import PyMongo

    mongo = PyMongo(app)
    app.mongo = mongo

    return app


def register_rq(app):
    from flask.ext.rq import RQ

    RQ(app)

    return app
