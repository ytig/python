#!/usr/local/bin/python3
import pymysql
from kit import hasvar, getvar, setvar
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
    assert hasvar(connect, '_cursors') or setvar(connect, '_cursors', set())
    var = getvar(connect, '_cursors')
    cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
    var.add(cursor)
    try:
        yield cursor
    except BaseException:
        var.remove(cursor)
        if not var:
            connect.rollback()
        cursor.close()
        raise
    else:
        var.remove(cursor)
        if not var:
            connect.commit()
        cursor.close()


Database = Connect.series(Cursor)
