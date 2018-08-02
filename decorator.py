#!/usr/local/bin/python3
import json
import inspect
import threading
from kit import module


class Closure:
    def __init__(self, closure):
        self.closure = closure

    # 解闭包
    def __call__(self):
        return self.closure()


class Lock:
    LOCK = threading.Lock()  # 全局锁

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
        if not hasattr(generics, name):
            setattr(generics, name, dict())
        attr = getattr(generics, name)
        if k not in attr:
            attr[k] = (threading.Lock(), [],)
        return attr.get(k)

    def __enter__(self):
        tn = threading.current_thread().name
        with __class__.LOCK:
            lock, stack, = self.__lock
            a = tn not in stack
            if not a:
                stack.append(tn)
        if a:
            lock.acquire()
            with __class__.LOCK:
                stack.append(tn)

    def __exit__(self, t, v, tb):
        with __class__.LOCK:
            lock, stack, = self.__lock
            stack.pop()
            r = len(stack) == 0
        if r:
            lock.release()

    def __call__(self, generics):
        if isinstance(generics, staticmethod):
            return staticmethod(self(generics.__func__))
        elif isinstance(generics, classmethod):
            return classmethod(self(generics.__func__))
        elif isinstance(generics, property):
            return property(fget=self(generics.fget), fset=self(generics.fset), fdel=self(generics.fdel))
        elif callable(generics):
            def wrapper(*args, **kwargs):
                with self:
                    return generics(*args, **kwargs)
            return wrapper


# 实例锁（栈帧回溯）
def ilock(k=None):
    i = Closure(lambda: inspect.currentframe().f_back.f_back.f_back.f_back.f_locals['args'][0])

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
    LOCK = threading.Lock()  # 全局锁
    QUAL = 0  # 唯一码

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
        if not hasattr(generics, name):
            setattr(generics, name, set())
        return getattr(generics, name)

    @staticmethod
    def __compile(a, b):
        if isinstance(b, str):
            def _a(*args, **kwargs):
                kwargs.update({b: False, })
                return a(*args, **kwargs)

            def _b(*args, **kwargs):
                kwargs.update({b: True, })
                return a(*args, **kwargs)
            return _a, _b
        else:
            if not callable(b):
                b = lambda *args, **kwargs: None
            return a, b

    def __call__(self, generics, r=None):
        if isinstance(generics, staticmethod):
            return staticmethod(self(generics.__func__, r=r))
        elif isinstance(generics, classmethod):
            return classmethod(self(generics.__func__, r=r))
        elif callable(generics):
            with __class__.LOCK:
                __class__.QUAL += 1
                qual = __class__.QUAL
            a, b, = __class__.__compile(generics, r)

            def wrapper(*args, **kwargs):
                throw = self.__throw
                if qual not in throw:
                    r = a(*args, **kwargs)
                    throw.add(qual)
                    return r
                else:
                    return b(*args, **kwargs)
            return wrapper


# 实例单次（栈帧回溯）
def ithrow(r=None):
    i = Closure(lambda: inspect.currentframe().f_back.f_back.f_back.f_locals['args'][0])

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
        @Lock(cls)
        def instanceOf(*args, **kwargs):
            key = json.dumps((args, kwargs,))
            if key not in instances:
                instances[key] = cls(*args, **kwargs)
            return instances[key]
        setattr(cls, fn, instanceOf)
        return cls
    return decorator
