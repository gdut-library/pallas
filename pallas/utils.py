#coding: utf-8

from contextlib import contextmanager

import pyisbn


def parse_isbn(isbn):
    '''生成 10 位和 13 位 isbn 码。
    如果 isbn 码转换失败，直接返回原来的输入

    :param isbn: 原始的 isbn
    '''
    try:
        isbn_a = pyisbn.convert(str(isbn))
        isbn_b = pyisbn.convert(isbn_a)

        result = {}
        result['isbn%d' % len(isbn_a)] = isbn_a
        result['isbn%d' % len(isbn_b)] = isbn_b
    except pyisbn.IsbnError:
        result = {'isbn10': isbn, 'isbn13': isbn}

    return result


@contextmanager
def ignores(*exceptions):
    try:
        yield
    except exceptions:
        pass
