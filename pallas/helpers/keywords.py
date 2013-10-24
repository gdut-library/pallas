#coding: utf-8

import re
from collections import defaultdict


__all__ = ['calculate']


def clean_author(author):
    result = re.compile(u'[\(\[\（].*[\]\)\）](.*)').findall(author)
    if result:
        author = result[0]
    return author.split()[0].strip()


def clean_price(price):
    pat = re.compile(u'^(CNY|USD|HKD|JPY){0,1}[^\d]*(\d+\.{0,1}\d{0,2}).*')
    result = pat.findall(price)
    unit, price = 'CNY', 0.0
    if result:
        unit, price = result[0]
    unit = unit or 'CNY'
    try:
        return (unit, float(price))
    except ValueError:
        return (unit, 0.0)


def clean_publisher(publisher):
    return publisher or u'未知出版社'


def calculate(books):
    authors = defaultdict(int)
    publishers = defaultdict(int)
    prices = defaultdict(int)

    for book in books:
        for author in book['author']:
            authors[clean_author(author)] += 1

        publishers[clean_publisher(book['publisher'])] += 1

        unit, price = clean_price(book['price'])
        prices[unit] += price

    return {
        'authors': authors,
        'publishers': publishers,
        'prices': prices
    }
