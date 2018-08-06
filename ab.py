#!/usr/local/bin/python3
import weakref
import inspect
from kit import unique, search, hasvar, getvar, setvar, frames, getargs, depth
from decorator import Lock, ilock, ithrow
from shutdown import bregister, aregister, unregister


# 定义类型
def define(super, ignore=None):
    args, kwargs, keywords, = getargs(fi=1, pattern=r'__new__')
    bases = tuple(search(lambda cls: cls.__bases__).depth(*args[2]))
    namespace = args[3]
    keywords.add('__class__')
    keywords.update(ignore or [])
    with frames(back=1) as f:
        assert f.has(0)
        assert '__class__' in f[0].f_locals
        __class__ = f[0].f_locals['__class__']
        with Lock(__class__):
            assert hasvar(__class__, '__unique__') or setvar(__class__, '__unique__', unique())
            __unique__ = getvar(__class__, '__unique__')
        for key in f[0].f_locals.keys():
            if key in keywords:
                continue
            var = f[0].f_locals[key]
            _var = None
            if key in namespace:
                _var = namespace.get(key)
            else:
                for b in bases:
                    if hasvar(b, key):
                        _var = getvar(b, key)
                        break
            if isinstance(var, staticmethod):
                var = var.__func__
                _var = _var.__func__ if isinstance(_var, staticmethod) else None
                namespace[key] = staticmethod(_fork(var, _var, str(__unique__) + '/staticmethod/' + key))
            elif isinstance(var, classmethod):
                var = var.__func__
                _var = _var.__func__ if isinstance(_var, classmethod) else None
                namespace[key] = classmethod(_fork(var, _var, str(__unique__) + '/classmethod/' + key))
            elif isinstance(var, property):
                fget, fset, fdel, = (var.fget, var.fset, var.fdel,)
                _fget, _fset, _fdel, = (_var.fget, _var.fset, _var.fdel,) if isinstance(_var, property) else (None, None, None,)
                namespace[key] = property(fget=_fork(fget, _fget, str(__unique__) + '/property.fget/' + key) if fget else None, fset=_fork(fset, _fset, str(__unique__) + '/property.fset/' + key) if fset else None, fdel=_fork(fdel, _fdel, str(__unique__) + '/property.fdel/' + key) if fdel else None)
            elif inspect.isfunction(var):
                _var = _var if inspect.isfunction(_var) else None
                namespace[key] = _fork(var, _var, str(__unique__) + '/function/' + key)
            else:
                namespace[key] = var
        return super.__new__(*args, **kwargs)


# 原始调用
def invoke(*d):
    with frames(filter=lambda f: f.f_code is _f_code) as f:
        assert f.has(0)
        if f[0].f_locals['old'] is not None:
            return f[0].f_locals['old'](*f[0].f_locals['args'], **f[0].f_locals['kwargs'])
        else:
            assert d
            return d[0]


def _fork(new, old, mark):
    def wrapper(*args, **kwargs):
        mark
        if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
            return new(*args, **kwargs)
        elif old is not None:
            return old(*args, **kwargs)
    return wrapper


_f_code = _fork(None, None, None).__code__


class weakmethod:
    GC = object()  # 已回收

    def __init__(self, obj, name):
        self.ref = weakref.ref(obj)
        self.name = name

    def __call__(self, *args, **kwargs):
        obj = self.ref()
        if obj is not None:
            return getattr(obj, self.name)(*args, **kwargs)
        else:
            return weakmethod.GC


class ABMeta(type):
    def __new__(cls, *args, **kwargs):
        def __init__(self, *args, **kwargs):
            setvar(self, '__weakbef__', weakmethod(self, '__bef__'))
            setvar(self, '__weakaft__', weakmethod(self, '__aft__'))
            ret = invoke(None)
            bregister(getvar(self, '__weakbef__'))
            aregister(getvar(self, '__weakaft__'))
            return ret

        def __bef__(self):
            return invoke(None)

        def __aft__(self):
            return invoke(None)

        @ilock()
        @ithrow()
        def __del__(self):
            unregister(getvar(self, '__weakaft__'))
            unregister(getvar(self, '__weakbef__'))
            return invoke(None)
        return define(super())
