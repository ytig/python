#!/usr/local/bin/python3
# coding:utf-8
import pymysql
from withs import *


class Connect:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.__connect = Stack()

    def __enter__(self):
        connect = pymysql.connect(*self.args, **self.kwargs)
        self.__connect.push(connect)
        return connect

    def __exit__(self, type, value, traceback):
        connect = self.__connect.pop()
        connect.close()


class Cursor:
    def __init__(self, connect):
        self.connect = connect
        self.__cursor = Stack()

    def __enter__(self):
        cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)
        self.__cursor.push(cursor)
        return cursor

    def __exit__(self, type, value, traceback):
        cursor = self.__cursor.pop()
        try:
            if type is None:
                self.connect.commit()
            else:
                self.connect.rollback()
        finally:
            cursor.close()


Database = withs(Connect, Cursor)
