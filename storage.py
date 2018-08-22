#!/usr/local/bin/python3
import os
import random
import pickle
import weakref
from kit import workspace
from decorator import instance


# 数据编码
def encode(obj, catch=False):
    hex = ''
    if obj is not None:
        try:
            hex = pickle.dumps(obj).hex()
        except BaseException:
            hex = ''
            if not catch:
                raise
    return hex


# 数据解码
def decode(hex, catch=False):
    obj = None
    if hex:
        try:
            obj = pickle.loads(bytes.fromhex(hex))
        except BaseException:
            obj = None
            if not catch:
                raise
    return obj


# 文件备份
def rf(path):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    while True:
        path = os.path.join(dirname, basename + '.' + str(random.randint(10000, 19999)))
        if not os.path.exists(path):
            return path


@instance()
class _Storage:
    def __init__(self, path):
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self._reader = {}
        self._writer = open(path, mode='a')
        self._dirty = False
        with open(path) as file:
            for line in file:
                item = decode(line.strip('\n'))
                if item[0] in self._reader:
                    self._dirty = True
                self._reader[item[0]] = item[1]

    def keys(self):
        return list(self._reader.keys())

    def get(self, key, defaultValue=None):
        assert isinstance(key, str)
        return self._reader.get(key, defaultValue)

    def set(self, key, value):
        assert isinstance(key, str)
        self._writer.write(encode((key, value,)) + '\n')
        self._writer.flush()
        if key in self._reader:
            self._dirty = True
        self._reader[key] = value

    def __del__(self):
        self._writer.close()
        if self._dirty:
            path = self._writer.name
            _path = rf(path)
            os.rename(path, _path)
            with open(path, mode='w') as file:
                for key, value, in self._reader.items():
                    file.write(encode((key, value,)) + '\n')
            os.remove(_path)
        del self._writer


class Storage:
    def __init__(self, path):
        if path.startswith('~/'):
            path = workspace() + '/.storage/' + path[2:]
        path = os.path.realpath(path)
        self._storage = weakref.ref(_Storage(path))

    # 轮询
    def keys(self):
        return self._storage().keys()

    # 读取
    def get(self, key, defaultValue=None):
        return self._storage().get(key, defaultValue=defaultValue)

    # 写入
    def set(self, key, value):
        return self._storage().set(key, value)
