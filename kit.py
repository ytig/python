#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
import inspect
PASS = object()  # 跳过


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


# 注入参数（装饰器）
def inject(segm=None, argv=sys.argv):
    args = []
    if argv:
        if segm is None:
            for arg in argv:
                if not args:
                    args.append(arg)
                else:
                    if arg.startswith('-'):
                        break
                    else:
                        args.append(arg)
        elif segm:
            for arg in argv[1:]:
                if not args:
                    if arg == '-':
                        break
                    elif arg == '-' + segm:
                        args.append(arg)
                else:
                    if arg.startswith('-'):
                        break
                    else:
                        args.append(arg)
        else:
            a = argv[1:]
            if '-' in a:
                args = a[a.index('-'):]

    def decorator(function):
        def wrapper():
            spec = inspect.getfullargspec(function)
            d = len(args) - len(spec.args)
            if d < 0:
                return function(*args + [None for i in range(-d)])
            elif d == 0 or spec.varargs is not None:
                return function(*args)
            else:
                return function(*args[:-d])
        return wrapper
    return decorator


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
