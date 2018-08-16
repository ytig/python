#!/usr/local/bin/python3
import inspect
from kit import getvar


# 切面
def aspect(wrapped):
    def wrapper(*args, **kwargs):
        try:
            wrapped = wrapper.__wrapped__
            i = inspect.signature(wrapped).bind(*args, **kwargs)
            for input in wrapper.__input__:
                i = input(i)
            o = wrapped(*i.args, **i.kwargs)
            for output in wrapper.__output__:
                o = output(i, o)
            return o
        except BaseException as e:
            for error in wrapper.__error__:
                try:
                    e = error(i, e)
                except BaseException:
                    pass
            raise e
    wrapper.__wrapped__ = wrapped
    wrapper.__input__ = []
    wrapper.__output__ = []
    wrapper.__error__ = []
    return wrapper


# 通知
class advice:
    @classmethod
    def __init_subclass__(cls, aspect=None, ret=False):
        assert aspect

        def input(i):
            var = getvar(cls, 'input')
            if isinstance(var, staticmethod):
                r = var.__func__(i)
                if ret:
                    return r
            return i
        aspect.__input__.append(input)

        def output(i, o):
            var = getvar(cls, 'output')
            if isinstance(var, staticmethod):
                r = var.__func__(i, o)
                if ret:
                    return r
            return o
        aspect.__output__.append(output)

        def error(i, e):
            var = getvar(cls, 'error')
            if isinstance(var, staticmethod):
                r = var.__func__(i, e)
                if ret:
                    return r
            return e
        aspect.__error__.append(error)
