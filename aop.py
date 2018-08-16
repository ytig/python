#!/usr/local/bin/python3
import inspect
from kit import getvar


# 切面
def aspect(obj):
    def wrapper(*args, **kwargs):
        try:
            w = wrapper.__wrapped__
            ba = inspect.signature(w).bind(*args, **kwargs)
            for c in wrapper.__input__:
                ba = c(ba)
            ret = w(*ba.args, **ba.kwargs)
            for c in wrapper.__output__:
                ret = c(ba, ret)
            return ret
        except BaseException as e:
            for c in wrapper.__error__:
                try:
                    e = c(ba, e)
                except BaseException:
                    pass
            raise e
    wrapper.__wrapped__ = obj
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
