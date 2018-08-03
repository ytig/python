#!/usr/local/bin/python3
import weakref
import inspect
from kit import search, hasvar, getvar, setvar
from decorator import ilock, ithrow
from shutdown import bregister, aregister, unregister


# 定义类
def define(super, ignore=['__class__']):
    def parse(f_locals):
        cls = f_locals['cls']
        args = f_locals['args']
        kwargs = f_locals['kwargs']
        __dict__ = dict((k, v,) for k, v, in f_locals.items() if k not in ['cls', 'args', 'kwargs', ] + ignore)
        return cls, args, kwargs, __dict__,
    cls, args, kwargs, __dict__, = parse(inspect.currentframe().f_back.f_locals)
    bases = tuple(search(lambda cls: cls.__bases__).depth(*args[1]))
    namespace = args[2]

    def _getvar(key, default=None):
        if key in namespace:
            return namespace.get(key)
        else:
            for b in bases:
                if hasvar(b, key):
                    return getvar(b, key)
        return default

    def _setvar(key, var):
        _var = _getvar(key)
        if isinstance(var, staticmethod):
            var = var.__func__
            _var = _var.__func__ if isinstance(_var, staticmethod) else None

            def __var__(*args, **kwargs):
                # todo
                pass
            namespace[key] = staticmethod(__var__)
        elif isinstance(var, classmethod):
            var = var.__func__
            _var = _var.__func__ if isinstance(_var, classmethod) else None

            def __var__(cls, *args, **kwargs):
                if cls is __class__:
                    return var(cls, _var, *args, **kwargs)
                elif _var is not None:
                    return _var(cls, *args, **kwargs)
            namespace[key] = classmethod(__var__)
        elif isinstance(var, property):
            fget, fset, fdel, = (var.fget, var.fset, var.fdel,)
            _fget, _fset, _fdel, = (_var.fget, _var.fset, _var.fdel,) if isinstance(_var, property) else (None, None, None,)
            if fget:
                def __fget__(self):
                    if self.__class__ is __class__:
                        return fget(self, _fget)
                    elif _fget is not None:
                        return _fget(self)
            else:
                __fget__ = None
            if fset:
                def __fset__(self, value):
                    if self.__class__ is __class__:
                        return fset(self, _fset, value)
                    elif _fset is not None:
                        return _fset(self, value)
            else:
                __fset__ = None
            if fdel:
                def __fdel__(self):
                    if self.__class__ is __class__:
                        return fdel(self, _fdel)
                    elif _fdel is not None:
                        return _fdel(self)
            else:
                __fdel__ = None
            namespace[key] = property(fget=__fget__, fset=__fset__, fdel=__fdel__)
        elif inspect.isfunction(var):
            _var = _var if inspect.isfunction(_var) else None

            def __var__(self, *args, **kwargs):
                if self.__class__ is __class__:
                    return var(self, _var, *args, **kwargs)
                elif _var is not None:
                    return _var(self, *args, **kwargs)
            namespace[key] = __var__
        else:
            namespace[key] = var
    for k, v, in __dict__.items():
        _setvar(k, v)
    __class__ = super.__new__(cls, *args, **kwargs)
    return __class__


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
        def __init__(*args, **kwargs):
            ret = None
            self = args[0]
            setvar(self, '__weakbef__', weakmethod(self, '__bef__'))
            setvar(self, '__weakaft__', weakmethod(self, '__aft__'))
            if args[1] is not None:
                ret = args[1](self, *args[2:], **kwargs)
            bregister(getvar(self, '__weakbef__'))
            aregister(getvar(self, '__weakaft__'))
            return ret

        def __bef__(*args, **kwargs):
            ret = None
            self = args[0]
            if args[1] is not None:
                ret = args[1](self, *args[2:], **kwargs)
            return ret

        def __aft__(*args, **kwargs):
            ret = None
            self = args[0]
            if args[1] is not None:
                ret = args[1](self, *args[2:], **kwargs)
            return ret

        @ilock()
        @ithrow()
        def __del__(*args, **kwargs):
            ret = None
            self = args[0]
            unregister(getvar(self, '__weakaft__'))
            unregister(getvar(self, '__weakbef__'))
            if args[1] is not None:
                ret = args[1](self, *args[2:], **kwargs)
            return ret
        return define(super())
