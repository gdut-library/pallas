#coding: utf-8

import requests
from flask import current_app

from pallas.app import build
from pallas.utils import parse_isbn


__all__ = ['sync_book']


def sync_book(isbn):
    if not isinstance(isbn, dict):
        isbn = parse_isbn(isbn)
    r = requests.get('https://api.douban.com/v2/book/isbn/%s' % isbn['isbn13'])
    if r.ok:
        app, result = build(), r.json()
        with app.app_context():
            current_app.mongo.db.books.update(isbn, result, upsert=True)
            return result
    return None
