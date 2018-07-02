#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
PASS = object()  # 跳过


# 绑定关键字参数
def bind(function, *binds, **kwbinds):
    def method(*args, **kwargs):
        args = list(args)
        for i in range(len(binds)):
            arg = binds[i]
            if arg is PASS:
                if i >= len(args):
                    raise Exception('pass argument missing.')
            else:
                args.insert(i, arg)
        kwargs.update(kwbinds)
        return function(*args, **kwargs)
    return method


# 工作区目录
def workspace():
    for module in sys.modules.values():
        if getattr(module, '__name__', '') == '__main__':
            if hasattr(module, '__file__'):
                return os.path.dirname(os.path.abspath(module.__file__))
            else:
                return os.path.abspath('')
