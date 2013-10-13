#coding: utf-8

from flask import current_app

import api

from pallas.utils import parse_isbn
from pallas.app import build
from .book import sync_book


__all__ = ['sync_user']


def sync_user(cardno, password):
    def _(record):
        record = record['details']
        return {
            'title': record['name'],
            'isbn': record['isbn'],
            'ctrlno': record['ctrlno'],
            'locations': record['locations'][0]['location']
        }

    app = build()
    with app.app_contect():

        me = api.Me()
        token = me.login(cardno, password).values()[0]

        personal = me.personal(token)
        personal['history'] = [_(i) for i in me.history(token, verbose=True)]

        current_app.mongo.db.users.update({'cardno': personal['cardno']},
                                          personal, upsert=True)

        for book in personal['history']:
            isbn = parse_isbn(book['isbn'])
            if not current_app.mongo.db.books.find(isbn):
                sync_book(isbn)
