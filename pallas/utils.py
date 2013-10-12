#coding: utf-8

from functools import wraps

from flask import session, url_for, redirect

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
