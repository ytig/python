#!/usr/local/bin/python3
import os
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


class Storage:
    def __init__(self, path):
        if path.startswith('~/'):
            path = workspace() + '/.storage/' + path[2:]
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self._reader = {}
        self._writer = open(path, mode='a')
        with open(path) as file:
            for line in file:
                item = decode(line.strip('\n'))
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
        self._reader[key] = value

    def __del__(self):
        if hasattr(self, '_writer'):
            self._writer.close()
            del self._writer
