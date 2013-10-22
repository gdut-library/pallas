#coding: utf-8

from functools import wraps
from collections import defaultdict

from fuzzywuzzy import process
from fuzzywuzzy.fuzz import WRatio

from pallas.utils import ignores


__all__ = ['calculate']


def _to_unicode(raw):
    if isinstance(raw, unicode):
        return raw
    with ignores(UnicodeEncodeError):
        raw = raw.decode('utf-8')
    return raw


def flatten(items):
    is_not_flatten = True
    while is_not_flatten:
        is_not_flatten = False

        for item in items:
            if isinstance(item, list):
                items.remove(item)
                items = items + item
                is_not_flatten = True

    # remove empty stuffs but not 0
    return filter(lambda x: x or x == 0, items)


def make_cleaner(func):
    @wraps(func)
    def wrapper(items):
        return flatten(map(func, items))
    return wrapper


def remove_char_cleaner(char):
    char = _to_unicode(char)

    @make_cleaner
    def remove_char(item):
        item = _to_unicode(item)
        return item.split(char)
    return remove_char


cleaners = [
    remove_char_cleaner(u'-'),
    remove_char_cleaner(u'—'),
    remove_char_cleaner(u'#'),
    make_cleaner(lambda x: x.lower())
]


def calculate(tags):
    '''计算 tag'''

    # 去除 tag 中多余的字符
    for cleaner in cleaners:
        tags = cleaner(tags)

    # 统计出现数目
    # 使用 fuzzywuzzy 来计算当前 tag 和已有的 tags 的相似度
    # 如果超过 70，使用已有的 tag
    buckets = defaultdict(int)
    for tag in tags:
        similar_tag = process.extractOne(tag, buckets.keys(),
                                         score_cutoff=70, scorer=WRatio)
        if similar_tag:
            tag = similar_tag[0]

        buckets[tag] = buckets[tag] + 1

    return buckets.items()
