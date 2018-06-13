#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
import json
from urllib.parse import quote, unquote


# 数据加密
def encode(value):
    return quote(json.dumps(value))


# 数据解密
def decode(value):
    return json.loads(unquote(value))


class Storage:
    def __init__(self, path):
        if path.startswith('~/'):
            path = os.path.dirname(os.path.abspath(sys.argv[0])) + '/.storage/' + path[2:]
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self._reader = {}
        self._writer = open(path, mode='a')
        with open(path, mode='r') as reader:
            key = None
            for line in reader:
                line = line.strip('\n')
                if key is None:
                    key = line
                else:
                    self._reader[key] = decode(line)
                    key = None

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
        self._writer.write(key + '\n' + encode(value) + '\n')
        self._writer.flush()
        self._reader[key] = value

    def __del__(self):
        if hasattr(self, '_writer'):
            self._writer.close()
            del self._writer
