#!/usr/local/bin/python3
# coding:utf-8
import pymysql
from withs import withs


class Connect:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        _connect = pymysql.connect(*self.args, **self.kwargs)
        self._connect = _connect
        return _connect

    def __exit__(self, type, value, traceback):
        _connect = self._connect
        del self._connect
        _connect.close()


class Cursor:
    def __init__(self, connect):
        self.connect = connect

    def __enter__(self):
        _cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)
        self._cursor = _cursor
        return _cursor

    def __exit__(self, type, value, traceback):
        _cursor = self._cursor
        del self._cursor
        try:
            if type is None:
                self.connect.commit()
            else:
                self.connect.rollback()
        finally:
            _cursor.close()


Database = withs(Connect, Cursor)
