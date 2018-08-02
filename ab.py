#!/usr/local/bin/python3
import weakref
import inspect
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
            return __class__.GC


class attribute:
    def __init__(self, bases, namespace):
        self.bases = bases
        self.namespace = namespace

    # 检查属性
    def hasattr(self, name):
        if name in self.namespace:
            return True
        for base in self.bases:
            if hasattr(base, name):
                return True
        return False

    # 获取属性
    def getattr(self, name, default=None):
        if name in self.namespace:
            return self.namespace.get(name)
        for base in self.bases:
            if hasattr(base, name):
                return getattr(base, name)
        return default

    # 设置属性
    def setattr(self, name, value):
        attr = self.getattr(name)
        if isinstance(value, staticmethod):
            new = value.__func__
            old = attr.__func__ if isinstance(attr, staticmethod) else None
            self.namespace[name] = staticmethod(lambda *args, **kwargs: new(old, *args, **kwargs))
        elif isinstance(value, classmethod):
            new = value.__func__
            old = attr.__func__ if isinstance(attr, classmethod) else None
            self.namespace[name] = classmethod(lambda cls, *args, **kwargs: new(cls, old, *args, **kwargs))
        elif isinstance(value, property):
            nget, nset, ndel, = (value.fget, value.fset, value.fdel,)
            oget, oset, odel, = (attr.fget, attr.fset, attr.fdel,) if isinstance(attr, property) else (None, None, None,)
            self.namespace[name] = property(fget=lambda self: nget(self, oget) if nget else None, fset=lambda self, value: nset(self, oset, value) if nset else None, fdel=lambda self: ndel(self, odel) if ndel else None)
        elif inspect.isfunction(value):
            new = value
            old = attr if inspect.isfunction(attr) else None
            self.namespace[name] = lambda self, *args, **kwargs: new(self, old, *args, **kwargs)
        else:
            self.namespace[name] = value


class ABMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        attr = attribute(bases, namespace)

        def __init__(self, *args, **kwargs):
            setattr(self, '__weakbef__', weakmethod(self, '__bef__'))
            setattr(self, '__weakaft__', weakmethod(self, '__aft__'))
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
            bregister(getattr(self, '__weakbef__'))
            aregister(getattr(self, '__weakaft__'))
        attr.setattr('__init__', __init__)

        def __bef__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        attr.setattr('__bef__', __bef__)

        def __aft__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        attr.setattr('__aft__', __aft__)

        @ilock()
        @ithrow()
        def __del__(self, *args, **kwargs):
            unregister(getattr(self, '__weakaft__'))
            unregister(getattr(self, '__weakbef__'))
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        attr.setattr('__del__', __del__)
        return super().__new__(mcls, name, bases, namespace, **kwargs)
