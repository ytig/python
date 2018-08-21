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
    hasattr(connect, '_cursors') or setattr(connect, '_cursors', set())
    _cursors = getattr(connect, '_cursors')
    cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
    _cursors.add(cursor)
    try:
        yield cursor
    except BaseException:
        _cursors.remove(cursor)
        if not _cursors:
            connect.rollback()
        cursor.close()
        raise
    else:
        _cursors.remove(cursor)
        if not _cursors:
            connect.commit()
        cursor.close()


Database = Connect.series(Cursor)
