#!/usr/local/bin/python3
import os
import random
import pickle
from kit import workspace


# 数据编码
def encode(object, catch=False):
    hex = ''
    if object is not None:
        try:
            hex = pickle.dumps(object).hex()
        except BaseException:
            hex = ''
            if not catch:
                raise
    return hex


# 数据解码
def decode(hex, catch=False):
    object = None
    if hex:
        try:
            object = pickle.loads(bytes.fromhex(hex))
        except BaseException:
            object = None
            if not catch:
                raise
    return object


# 文件备份
def rf(path):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    while True:
        path = os.path.join(dirname, basename + '.' + str(random.randint(10000, 19999)))
        if not os.path.exists(path):
            return path


class Storage:
    def __init__(self, path):
        if path.startswith('~/'):
            path = workspace() + '/.storage/' + path[2:]
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

    # 轮询
    def keys(self):
        return list(self._reader.keys())

    # 读取
    def get(self, key, defaultValue=None):
        return self._reader.get(key, defaultValue)

    # 写入
    def set(self, key, value):
        if not isinstance(key, str):
            raise Exception('key must be str.')
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
            with open(path, 'w') as file:
                for key, value, in self._reader.items():
                    file.write(encode((key, value,)) + '\n')
            os.remove(_path)
        del self._writer
