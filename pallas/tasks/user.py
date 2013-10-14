#coding: utf-8

import logging
from flask import current_app
from rq import get_current_job
from time import time

import api

from pallas.app import build
from pallas.utils import parse_isbn

from .book import sync_book


__all__ = ['sync_user']

logger = logging.getLogger('app')


def sync_user(cardno, password):
    '''同步用户信息

    :param cardno: 用户卡号
    :param password: 用户密码
    '''
    def _h(r):
        record = r['details']
        return {
            'title': record['name'],
            'isbn': str(record['isbn'].strip()),
            'ctrlno': record['ctrlno'],
            'locations': record['locations'][0]['location'],
            'borrowed_date': r['borrowed_date'],
            'returned_date': r['returned_date']
        }

    def _b(r):
        record = r['details']
        return {
            'title': record['name'],
            'isbn': str(record['isbn'].strip()),
            'ctrlno': record['ctrlno'],
            'locations': record['locations'][0]['location'],
            'borrowed_date': r['borrowed_date'],
            'deadline': r['deadline']
        }

    def update_progress(job, incr=0.1):
        job.meta['progress'] = min(1, incr + job.meta['progress'])
        job.save()

    job = get_current_job()
    job.meta['progress'] = 0

    with build().app_context():
        # 登录到图书馆
        logger.info('logging into library')
        me = api.Me()
        token = me.login(cardno, password).values()[0]
        update_progress(job)

        # 获取用户信息
        logger.info('fetching user infomations')
        personal = current_app.mongo.db.users.find_one({'cardno': cardno}) or \
            me.personal(token)
        update_progress(job)

        # 获取借阅历史
        #
        # TODO 查询最新的几页，而不是全部查询
        # 或者使用更好的判断算法减少查询量
        logger.info('fetching reading history')
        personal['reading'] = [_b(i) for i in me.borrowed(token, verbose=True)]
        # 如果借阅过的书籍在已借出的列表中当作在读
        reading_ctrlno = [i['ctrlno'] for i in personal['reading']]
        personal['history'] = [_h(i) for i in me.history(token, verbose=True)
                               if i['ctrlno'] not in reading_ctrlno]

        # 修改更新时间
        personal['last_updated'] = time()

        current_app.mongo.db.users.update({'cardno': cardno}, personal,
                                          upsert=True)
        update_progress(job, 0.3)

        # 获取没有记录的图书信息
        logger.info('fetching book informations')
        for book in personal['reading'] + personal['history']:
            isbn = parse_isbn(book['isbn'])
            if not current_app.mongo.db.books.find(isbn).count():
                sync_book(isbn)
        update_progress(job, 0.5)

        logger.info('sync for %s finish' % cardno)
        return personal
