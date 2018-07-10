#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
import inspect
PASS = object()  # 跳过


# 脚本参数
def arguments(segment, *strict):
    if not segment:
        segment = sys.argv[0]
    else:
        segment = '-' + segment
    args = None
    for arg in sys.argv:
        if args is not None:
            if arg.startswith('-'):
                break
            else:
                args.append(arg)
        elif arg == segment:
            args = []
    if strict:
        if args is None:
            args = []
        args = [strict[i](args[i] if i < len(args) else None) for i in range(len(strict))]
    return args


# 空值处理
def ifnone(generics):
    def d():
        if callable(generics):
            return generics()
        else:
            return generics
    return lambda arg: arg if arg is not None else d()


# 绑定参数
def bind(*args, **kwargs):
    call = args[0] if len(args) else None
    if not callable(call):
        raise Exception('callable missing.')
    extends = args[1:]
    updates = kwargs

    def bound(*args, **kwargs):
        args = list(args)
        for i in range(len(extends)):
            arg = extends[i]
            if arg is PASS:
                if i >= len(args):
                    raise Exception('argument missing.')
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
