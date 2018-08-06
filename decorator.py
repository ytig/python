#!/usr/local/bin/python3
import json
import inspect
import threading
from kit import bind, unique, hasvar, getvar, setvar, frames, module


class Closure:
    def __init__(self, closure):
        self.closure = closure

    # 解闭包
    def __call__(self):
        return self.closure()


class _Lock:
    LOCK = threading.Lock()  # 构建锁

    def __init__(self):
        self.lock = threading.Lock()
        self.stack = []

    def __enter__(self):
        tn = threading.current_thread().name
        with _Lock.LOCK:
            a = tn not in self.stack
            if not a:
                self.stack.append(tn)
        if a:
            self.lock.acquire()
            with _Lock.LOCK:
                self.stack.append(tn)

    def __exit__(self, t, v, tb):
        with _Lock.LOCK:
            self.stack.pop()
            r = len(self.stack) == 0
        if r:
            self.lock.release()


class Lock:
    LOCK = threading.Lock()  # 构建锁

    def __init__(self, generics, k=None):
        self.generics = generics
        self.k = k if isinstance(k, str) else ''

    @property
    def __lock(self):
        generics = self.generics
        k = self.k
        while isinstance(generics, Closure):
            generics = generics()
        if inspect.ismodule(generics):
            name = '__LOCK__'
        elif inspect.isclass(generics):
            name = '__Lock__'
        else:
            name = '__lock__'
        with Lock.LOCK:
            assert hasvar(generics, name) or setvar(generics, name, dict())
            var = getvar(generics, name)
            if k not in var:
                var[k] = _Lock()
            return var[k]

    def __enter__(self):
        self.__lock.__enter__()

    def __exit__(self, t, v, tb):
        self.__lock.__exit__(t, v, tb)

    # 装饰锁
    def __call__(self, generics):
        def decorator(call):
            def wrapper(*args, **kwargs):
                with self:
                    return call(*args, **kwargs)
            return wrapper
        if callable(generics):
            return decorator(generics)
        elif isinstance(generics, staticmethod):
            return staticmethod(decorator(generics.__func__))
        elif isinstance(generics, classmethod):
            return classmethod(decorator(generics.__func__))
        elif isinstance(generics, property):
            if generics.fdel:
                return property(fget=generics.fget, fset=generics.fset, fdel=decorator(generics.fdel))
            elif generics.fset:
                return property(fget=generics.fget, fset=decorator(generics.fset), fdel=generics.fdel)
            elif generics.fget:
                return property(fget=decorator(generics.fget), fset=generics.fset, fdel=generics.fdel)
            else:
                return generics


# 实例锁（栈帧回溯）
def ilock(k=None):
    i = Closure(lambda: frames()[4].f_locals['args'][0])

    def lock(generics):
        return Lock(i, k=k)(generics)
    return lock


# 类型锁（闭包传值）
def clock(closure, k=None):
    c = Closure(closure)

    def lock(generics):
        return Lock(c, k=k)(generics)
    return lock


# 模块锁
def mlock(k=None):
    m = module(ios=2)

    def lock(generics):
        return Lock(m, k=k)(generics)
    return lock


class Throw:
    def __init__(self, generics):
        self.generics = generics

    @property
    def __throw(self):
        generics = self.generics
        while isinstance(generics, Closure):
            generics = generics()
        if inspect.ismodule(generics):
            name = '__THROW__'
        elif inspect.isclass(generics):
            name = '__Throw__'
        else:
            name = '__throw__'
        assert hasvar(generics, name) or setvar(generics, name, set())
        return getvar(generics, name)

    # 装饰单次
    def __call__(self, generics, r=None):
        def decorator(call):
            id = unique()
            if isinstance(r, str):
                a = bind(call, **{r: False, })
                b = bind(call, **{r: True, })
            else:
                a = call
                b = r if callable(r) else lambda *args, **kwargs: None

            def wrapper(*args, **kwargs):
                throw = self.__throw
                if id not in throw:
                    ret = a(*args, **kwargs)
                    throw.add(id)
                    return ret
                else:
                    return b(*args, **kwargs)
            return wrapper
        if callable(generics):
            return decorator(generics)
        elif isinstance(generics, staticmethod):
            return staticmethod(decorator(generics.__func__))
        elif isinstance(generics, classmethod):
            return classmethod(decorator(generics.__func__))
        elif isinstance(generics, property):
            if generics.fdel:
                return property(fget=generics.fget, fset=generics.fset, fdel=decorator(generics.fdel))
            elif generics.fset:
                return property(fget=generics.fget, fset=decorator(generics.fset), fdel=generics.fdel)
            elif generics.fget:
                return property(fget=decorator(generics.fget), fset=generics.fset, fdel=generics.fdel)
            else:
                return generics


# 实例单次（栈帧回溯）
def ithrow(r=None):
    i = Closure(lambda: frames()[3].f_locals['args'][0])

    def throw(generics):
        return Throw(i)(generics, r=r)
    return throw


# 类型单次（闭包传值）
def cthrow(closure, r=None):
    c = Closure(closure)

    def throw(generics):
        return Throw(c)(generics, r=r)
    return throw


# 模块单次
def mthrow(r=None):
    m = module(ios=2)

    def throw(generics):
        return Throw(m)(generics, r=r)
    return throw


# 单例类型（同参）
def instance(fn='instanceOf'):
    def decorator(cls):
        instances = {}

        @staticmethod
        def instanceOf(*args, **kwargs):
            key = json.dumps((args, sorted(kwargs.items(), key=lambda i: i[0]),))
            with Lock(cls):
                if key not in instances:
                    instances[key] = cls(*args, **kwargs)
                return instances[key]
        assert not hasvar(cls, fn) and setvar(cls, fn, instanceOf)
        return cls
    return decorator
