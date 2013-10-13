#coding: utf-8

from functools import wraps

from flask import session, url_for, redirect

import pyisbn

import api


def check_login():
    return api.Me().check_login(session.get('token', ''))


class LoginRequired(object):

    def make_wrapper(self, func, check_cb):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not check_cb():
                return redirect(url_for('user.login', next=self.next or '/'))
            return func(*args, **kwargs)
        return wrapper

    def __init__(self, next=None):
        self.next = next

    def __call__(self, func):
        return self.make_wrapper(func, lambda: session.get('token', None))


class LibraryLoginRequired(LoginRequired):

    def __call__(self, func):
        return self.make_wrapper(func, check_login)


def parse_isbn(isbn):
    '''生成 10 位和 13 位 isbn 码。
    如果 isbn 码转换失败，直接返回原来的输入

    :param isbn: 原始的 isbn
    '''
    try:
        isbn_a = pyisbn.convert(isbn)
        isbn_b = pyisbn.convert(isbn_a)

        result = {}
        result['isbn%d' % len(isbn_a)] = isbn_a
        result['isbn%d' % len(isbn_b)] = isbn_b
    except pyisbn.IsbnError:
        result = {'isbn10': isbn, 'isbn13': isbn}

    return result
