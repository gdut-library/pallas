#coding: utf-8

from functools import wraps
from flask import session, redirect, url_for, abort, g

import api


__all__ = ['check_login', 'LoginRequired', 'LibraryLoginRequired',
           'ApiLoginRequired', 'api_login_required']


def check_login():
    '''检查当前用户登录 token 是否有效'''

    # TODO handle LibraryXXXError
    return api.Me().check_login(session.get('token', ''))


class LoginRequired(object):
    '''检查当前用户是否登录

    :param next: 登录后的跳转页
    '''

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
        return self.make_wrapper(func, lambda: g.user)


class LibraryLoginRequired(LoginRequired):
    '''检查当前用户的 token 是否有效

    :param next: 登录后的跳转页
    '''

    def __call__(self, func):
        return self.make_wrapper(func, check_login)


class ApiLoginRequired(LoginRequired):
    '''检查当前用户是否登录，
    未登录则返回 403 禁止调用接口'''

    def make_wrapper(self, func, check_cb):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not check_cb():
                abort(403)
            return func(*args, **kwargs)
        return wrapper

api_login_required = ApiLoginRequired()
