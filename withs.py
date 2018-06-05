#!/usr/local/bin/python3
# coding:utf-8


def _with2(parent, child):
    class family:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            _parent = parent(*self.args, **self.kwargs)
            torch = _parent.__enter__()
            try:
                _child = child(torch)
                torch = _child.__enter__()
                self.parent = _parent
                self.child = _child
                return torch
            except BaseException as e:
                _parent.__exit__(e.__class__, e, e.__traceback__)
                raise e

        def __exit__(self, type, value, traceback):
            _child = self.child
            del self.child
            _parent = self.parent
            del self.parent
            try:
                _child.__exit__(type, value, traceback)
            except BaseException as e:
                _parent.__exit__(e.__class__, e, e.__traceback__)
                raise e
            _parent.__exit__(type, value, traceback)
    return family


# 异常处理器嵌套
def withs(*args):
    l = len(args)
    if l <= 0:
        return None
    elif l == 1:
        return args[0]
    else:
        args = list(args)
        args[0] = _with2(args.pop(0), args[0])
        return withs(*args)
