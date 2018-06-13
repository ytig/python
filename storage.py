#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
import codecs


class Storage:
    def __init__(self, path):
        if path.startswith('~/'):
            path = os.path.dirname(os.path.abspath(sys.argv[0])) + '/.storage/' + path[2:]
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self._reader = {}
        self._writer = codecs.open(path, 'a', encoding='utf-8')
        reader = codecs.open(path, 'r', encoding='utf-8')
        key = None
        for line in reader:
            line = line.strip('\n')
            if key is None:
                key = line
            else:
                self._reader[key] = line
                key = None
        reader.close()

    # 轮询
    def keys(self):
        return self._reader.keys()

    # 读取
    def read(self, key, defaultValue=None):
        value = self._reader.get(key)
        return value if value is not None else defaultValue

    # 写入
    def write(self, key, value):
        self._writer.write(key)
        self._writer.write('\n')
        self._writer.write(value)
        self._writer.write('\n')
        self._writer.flush()
        self._reader[key] = value

    def __del__(self):
        if hasattr(self, '_writer'):
            self._writer.close()
            del self._writer
