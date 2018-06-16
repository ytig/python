#!/usr/local/bin/python3
# coding:utf-8
import pymysql
from wa import extends


@extends
class Connect:
    def __init__(self, *args, **kwargs):
        self.connect = pymysql.connect(*args, **kwargs)

    def __enter__(self):
        return self.connect

    def __exit__(self, type, value, traceback):
        self.connect.close()


@extends
class Cursor:
    def __init__(self, connect):
        self.connect = connect
        self.cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        return self.cursor

    def __exit__(self, type, value, traceback):
        try:
            if type is None:
                self.connect.commit()
            else:
                self.connect.rollback()
        finally:
            self.cursor.close()


Database = Connect.series(Cursor)
