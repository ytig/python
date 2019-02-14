#!/usr/local/bin/python3
import json
import pymysql
import threading
from remedy import *
from kit import hasvar, getvar, setvar
from decorator import _Lock, Lock, ilock
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


class Data:
    NO_PRIMARY = object()  # 临时模式

    def __init__(self, database, table, primary):
        self._database = database
        self._table = table
        self._primary = primary
        self._data = ''

    # 主键
    @ilock()
    @property
    def primary(self):
        if self._primary is Data.NO_PRIMARY:
            return None
        if self._primary is None:
            with Database(**self._database) as cursor:
                cursor.execute('insert into ' + self._table + ' (data) values (%s)', ('',))
                lastrowid = cursor.lastrowid
            self._primary = lastrowid
        return int(self._primary)

    # 删档
    def kill(self):
        primary = self.primary
        if primary is not None:
            with Database(**self._database) as cursor:
                cursor.execute('update ' + self._table + ' set deathday=current_timestamp where id=%s', (primary,))

    # 局域
    def scope(self, name):
        return type(self).Scope(self, name)

    class Scope:
        def __init__(self, data, name):
            self._data = data
            self._name = name

        # 读取
        def loads(self):
            primary = self._data.primary
            if primary is not None:
                with Database(**self._data._database) as cursor:
                    cursor.execute('select data from ' + self._data._table + ' where id=%s', (primary,))
                    row = cursor.fetchone()
                    return json.loads((row['data'] if row else None) or '{}').get(self._name, {})
            else:
                with Lock(self._data):
                    return json.loads(self._data._data or '{}').get(self._name, {})

        # 保存
        def saves(self, updates):
            primary = self._data.primary
            if primary is not None:
                with Database(**self._data._database) as cursor:
                    cursor.execute('select data from ' + self._data._table + ' where id=%s for update', (primary,))
                    row = cursor.fetchone()
                    obj = json.loads((row['data'] if row else None) or '{}')
                    if updates is None:
                        if self._name in obj:
                            obj.pop(self._name)
                    else:
                        obj[self._name] = value_not_none(safe_sum(obj.get(self._name, {}), updates))
                        if not obj[self._name]:
                            obj.pop(self._name)
                    cursor.execute('update ' + self._data._table + ' set data=%s where id=%s', (json.dumps(obj) if obj else '', primary,))
            else:
                with Lock(self._data):
                    obj = json.loads(self._data._data or '{}')
                    if updates is None:
                        if self._name in obj:
                            obj.pop(self._name)
                    else:
                        obj[self._name] = value_not_none(safe_sum(obj.get(self._name, {}), updates))
                        if not obj[self._name]:
                            obj.pop(self._name)
                    self._data._data = json.dumps(obj) if obj else ''

        # 读取
        def load(self, key, defaultValue=None):
            return self.loads().get(key, defaultValue)

        # 保存
        def save(self, key, value):
            return self.saves({key: value, })


class Data2:
    class Value(_Lock):
        def __init__(self, value):
            super().__init__()
            self.value = value

        def __enter__(self):
            super().__enter__()
            return self.value

    def __init__(self):
        self._data = {}
        self._wait = {}

    # 增
    @ilock()
    def insert(self, key, value):
        if key in self._data:
            raise KeyError
        value = type(self).Value(value)
        self._data[key] = value
        if key in self._wait:
            wait = self._wait.pop(key)
            wait.value = value
            wait.set()

    # 删
    @ilock()
    def delete(self, key):
        if key in self._data:
            return self._data.pop(key)

    # 改
    def update(self, key, timeout=None):
        with Lock(self):
            if key in self._data:
                return self._data[key]
            else:
                if key not in self._wait:
                    self._wait[key] = threading.Event()
                wait = self._wait[key]
        if not wait.wait(timeout=timeout):
            raise TimeoutError
        return wait.value

    # 查
    def select(self, key, timeout=None):
        with self.update(key, timeout=timeout) as value:
            return json.loads(json.dumps(value))
