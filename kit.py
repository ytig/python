#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
import inspect
PASS = object()  # 跳过


# 异常追溯
def trace():
    try:
        file = inspect.trace()[-1][1]
        for module in sys.modules.values():
            if getattr(module, '__file__', '') == file:
                return module
    except BaseException:
        pass
    return None


# 绑定参数
def bind(call, *extends, **updates):
    def bound(*args, **kwargs):
        args = list(args)
        for i in range(len(extends)):
            arg = extends[i]
            if arg is PASS:
                if i >= len(args):
                    raise Exception('pass argument missing.')
            else:
                args.insert(i, arg)
        kwargs.update(updates)
        return call(*args, **kwargs)
    return bound


# 工作区目录
def workspace():
    for module in sys.modules.values():
        if getattr(module, '__name__', '') == '__main__':
            if hasattr(module, '__file__'):
                return os.path.dirname(os.path.abspath(module.__file__))
            else:
                return os.path.abspath('')
