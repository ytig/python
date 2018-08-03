#!/usr/local/bin/python3
import weakref
import inspect
from kit import search, hasvar, getvar, setvar
from decorator import ilock, ithrow
from shutdown import bregister, aregister, unregister


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


class build:
    def __init__(self, bases, namespace):
        self.bases = tuple(search(lambda cls: cls.__bases__).depth(*bases))
        self.namespace = namespace

    # 检查变量
    def hasvar(self, k):
        if k in self.namespace:
            return True
        for b in self.bases:
            if hasvar(b, k):
                return True
        return False

    # 获取变量
    def getvar(self, k, d=None):
        if k in self.namespace:
            return self.namespace.get(k)
        for b in self.bases:
            if hasvar(b, k):
                return getvar(b, k)
        return d

    # 设置变量
    def setvar(self, k, v):
        var = self.getvar(k)
        if isinstance(v, staticmethod):
            new = v.__func__
            old = var.__func__ if isinstance(var, staticmethod) else None
            self.namespace[k] = staticmethod(lambda *args, **kwargs: new(old, *args, **kwargs))
        elif isinstance(v, classmethod):
            new = v.__func__
            old = var.__func__ if isinstance(var, classmethod) else None
            self.namespace[k] = classmethod(lambda cls, *args, **kwargs: new(cls, old, *args, **kwargs))
        elif isinstance(v, property):
            nget, nset, ndel, = (v.fget, v.fset, v.fdel,)
            oget, oset, odel, = (var.fget, var.fset, var.fdel,) if isinstance(var, property) else (None, None, None,)
            self.namespace[k] = property(fget=lambda self: nget(self, oget) if nget else None, fset=lambda self, value: nset(self, oset, value) if nset else None, fdel=lambda self: ndel(self, odel) if ndel else None)
        elif inspect.isfunction(v):
            new = v
            old = var if inspect.isfunction(var) else None
            self.namespace[k] = lambda self, *args, **kwargs: new(self, old, *args, **kwargs)
        else:
            self.namespace[k] = v


class ABMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        builder = build(bases, namespace)

        def __init__(self, *args, **kwargs):
            setvar(self, '__weakbef__', weakmethod(self, '__bef__'))
            setvar(self, '__weakaft__', weakmethod(self, '__aft__'))
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
            bregister(getvar(self, '__weakbef__'))
            aregister(getvar(self, '__weakaft__'))
        builder.setvar('__init__', __init__)

        def __bef__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        builder.setvar('__bef__', __bef__)

        def __aft__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        builder.setvar('__aft__', __aft__)

        @ilock()
        @ithrow()
        def __del__(self, *args, **kwargs):
            unregister(getvar(self, '__weakaft__'))
            unregister(getvar(self, '__weakbef__'))
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        builder.setvar('__del__', __del__)
        return super().__new__(mcls, name, bases, namespace, **kwargs)
