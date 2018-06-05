#!/usr/local/bin/python3
# coding:utf-8
import pymysql
from withs import withs


class connect:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        self.connect = pymysql.connect(*self.args, **self.kwargs)
        return self.connect

    def __exit__(self, type, value, traceback):
        _connect = self.connect
        del self.connect
        _connect.close()


class cursor:
    def __init__(self, connect):
        self.connect = connect

    def __enter__(self):
        self.cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)
        return self.cursor

    def __exit__(self, type, value, traceback):
        _cursor = self.cursor
        del self.cursor
        try:
            if type is None:
                self.connect.commit()
            else:
                self.connect.rollback()
        finally:
            _cursor.close()
