#coding: utf-8

import re
import logging
from flask import current_app
from rq import get_current_job
import time

from api.base import LIBRARY_URL

from pallas.app import build
from pallas.utils import parse_isbn
from pallas.helpers import tags

from .user import sync_user


__all__ = ['generate_report']


logger = logging.getLogger('tasks')


def calculate_tags(books):
    '''计算标签'''
    return tags.calculate([i['name'] for book in books for i in book['tags']])


def calculate_keywords(books):
    '''计算作者、出版社、价格等关键字'''
    def _clean_author(author):
        result = re.compile(u'[\(\[].*[\]\)](.*)').findall(author)
        if result:
            author = result[0]
        return author.strip()

    def _clean_price(price):
        # TODO 支持更多的货币单位
        result = re.compile(u'([\d]+\.{0,1}[\d]{0,2}).*').findall(price)
        if result:
            price = result[0]
        try:
            return ('CNY', float(price))
        except ValueError:
            # convert to float
            return ('CNY', 0.0)

    result = {
        'authors': [],  # (name, count) pairs
        'publishers': [],  # (name, count) pairs
        'price': {
            'CNY': 0.0,
        }
    }

    authors, publishers = {}, {}
    for book in books:
        for a in book['author']:
            a = _clean_author(a)
            authors[a] = authors.get(a, 0) + 1

        p = book['publisher'] or u'未知出版社'
        publishers[p] = publishers.get(p, 0) + 1

        m, price = _clean_price(book['price'])
        result['price'][m] = result['price'].get(m, 0.0) + price

    result['authors'] = authors.items()
    result['publishers'] = publishers.items()

    return result


def generate_report(cardno, password):
    '''生成报表'''
    library_url = lambda x: LIBRARY_URL + 'bookinfo.aspx?ctrlno=' + x
    search_list = lambda l, cond: next((x for x in l if cond(x)), None)
    remove_none = lambda l: filter(None, l)

    def _reading(raw, reading):
        key = 'isbn13' if len(raw['isbn']) == 13 else 'isbn10'
        book = search_list(reading, lambda x: x[key] == raw['isbn'])
        if not book:
            return
        book['borrowed_date'] = raw['borrowed_date']
        book['library_url'] = library_url(raw['ctrlno'])
        return book

    def _history(raw, history):
        book = _reading(raw, history)
        if not book:
            return
        book['returned_date'] = raw['returned_date']
        return book

    job = get_current_job()
    job.meta['progress'] = 0.0

    with build().app_context():
        report = {
            'cardno': cardno
        }

        # 更新用户信息
        user = sync_user(cardno, password)
        job.meta['progress'] = 0.5

        # 获取书籍列表
        logger.info('fetching books')
        get_isbn = lambda x: [parse_isbn(i['isbn'])['isbn13'] for i in x]
        get_book = lambda isbn: remove_none([i for i in
            current_app.mongo.db.books.find({'isbn13': {'$in': isbn}},
                                            {'_id': False})])
        history = get_book(get_isbn(user['history']))
        reading = get_book(get_isbn(user['reading']))
        all_books = history + reading
        job.meta['progress'] = 0.7

        # 阅读记录
        logger.info('generate reading record')
        report['history'] = remove_none([_history(i, history)
                                         for i in user['history']])
        report['reading'] = remove_none([_reading(i, reading)
                                         for i in user['reading']])
        job.meta['progress'] = 0.8

        # 关键字和 tag
        logger.info('generate keywords & tags')
        report['keywords'] = calculate_keywords(all_books)
        report['tags'] = calculate_tags(all_books)

        current_app.mongo.db.reports.update({'cardno': cardno}, report,
                                            upsert=True)
        job.meta['progress'] = 1.0

        # 设定下次更新时间
        # TODO 归类到另一个 job 中，但是要等 rq 0.4.0
        current_app.mongo.db.users.update({'cardno': cardno}, {
            '$set': {'last_updated': time.time()}
        })

        return report
