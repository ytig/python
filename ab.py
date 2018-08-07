#!/usr/local/bin/python3
import weakref
import inspect
from kit import unique, search, hasvar, getvar, setvar, frames, getargs, depth
from decorator import Lock, ilock, ithrow
from shutdown import bregister, aregister, unregister


# 定义类型
def define(super, ignore=None):
    args, kwargs, keywords, = getargs(pattern=r'__new__', back=1)
    assert None not in (args, kwargs, keywords,)
    bases = tuple(search(lambda cls: cls.__bases__).depth(*args[2]))
    namespace = args[3]
    keywords.update(ignore or [])
    with frames(back=1) as f:
        assert f.has(0)
        assert '__class__' in f[0].f_code.co_freevars
        __class__ = f[0].f_locals['__class__']
        with Lock(__class__):
            assert hasvar(__class__, '__unique__') or setvar(__class__, '__unique__', unique())
            __unique__ = getvar(__class__, '__unique__')
        for key in f[0].f_code.co_varnames + f[0].f_code.co_cellvars:
            if key in keywords:
                continue

            def decorator(new, old, name=''):
                if inspect.isfunction(new):
                    mark = '/'.join((__unique__, key, name,))
                    if inspect.isgeneratorfunction(new):
                        if not inspect.isgeneratorfunction(old):
                            old = None
                        return _generatorfunction(new, old, mark)
                    else:
                        if not inspect.isfunction(old):
                            old = None
                        return _function(new, old, mark)
                else:
                    return old
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
                namespace[key] = staticmethod(decorator(var, _var))
            elif isinstance(var, classmethod):
                var = var.__func__
                _var = _var.__func__ if isinstance(_var, classmethod) else None
                namespace[key] = classmethod(decorator(var, _var))
            elif isinstance(var, property):
                fget, fset, fdel, = (var.fget, var.fset, var.fdel,)
                _fget, _fset, _fdel, = (_var.fget, _var.fset, _var.fdel,) if isinstance(_var, property) else (None, None, None,)
                namespace[key] = property(fget=decorator(fget, _fget, name='fget'), fset=decorator(fset, _fset, name='fset'), fdel=decorator(fdel, _fdel, name='fdel'))
            elif inspect.isfunction(var):
                namespace[key] = decorator(var, _var)
            else:
                namespace[key] = var
        return super.__new__(*args, **kwargs)


# 原始调用
def invoke(*d):
    with frames(filter=lambda f: f.f_code in _f_codes) as f:
        assert f.has(0)
        if f[0].f_locals['old'] is not None:
            return f[0].f_locals['old'](*f[0].f_locals['args'], **f[0].f_locals['kwargs'])
        else:
            assert d
            return d[0]


def _function(new, old, mark):
    def wrapper(*args, **kwargs):
        mark
        if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
            return new(*args, **kwargs)
        elif old is not None:
            return old(*args, **kwargs)
    return wrapper


def _generatorfunction(new, old, mark):
    def wrapper(*args, **kwargs):
        mark
        if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
            value = yield from new(*args, **kwargs)
            return value
        elif old is not None:
            value = yield from old(*args, **kwargs)
            return value
    return wrapper


_f_codes = (_function(None, None, None).__code__, _generatorfunction(None, None, None).__code__,)


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
