#!/usr/local/bin/python3
import pymysql
from wa import withas


@withas
def Connect(*args, **kwargs):
    connect = pymysql.connect(*args, **kwargs)
    try:
        yield connect
    finally:
        connect.close()


@withas
def Cursor(connect):
    cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    except BaseException:
        connect.rollback()
        raise
    else:
        connect.commit()
    finally:
        cursor.close()


Database = Connect.series(Cursor)
