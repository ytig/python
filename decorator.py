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

    def __init__(self, generics):
        self.generics = generics

    @property
    def __lock(self):
        generics = self.generics
        while isinstance(generics, Closure):
            generics = generics()
        if inspect.ismodule(generics):
            name = '__LOCK__'
        elif inspect.isclass(generics):
            name = '__Lock__'
        else:
            name = '__lock__'
        if not hasattr(generics, name):
            setattr(generics, name, (threading.Lock(), [],))
        return getattr(generics, name)

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
def ilock():
    i = Closure(lambda: inspect.currentframe().f_back.f_back.f_back.f_back.f_locals['args'][0])

    def lock(generics):
        return Lock(i)(generics)
    return lock


# 类型锁（闭包传值）
def clock(closure):
    c = Closure(closure)

    def lock(generics):
        return Lock(c)(generics)
    return lock


# 模块锁
def mlock():
    m = module(ios=2)

    def lock(generics):
        return Lock(m)(generics)
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

    def __call__(self, generics, repeat):
        if isinstance(generics, staticmethod):
            return staticmethod(self(generics.__func__, repeat))
        elif isinstance(generics, classmethod):
            return classmethod(self(generics.__func__, repeat))
        elif callable(generics):
            with __class__.LOCK:
                __class__.QUAL += 1
                qual = __class__.QUAL
            a, b, = __class__.__compile(generics, repeat)

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
def ithrow(repeat=None):
    i = Closure(lambda: inspect.currentframe().f_back.f_back.f_back.f_locals['args'][0])

    def throw(generics):
        return Throw(i)(generics, repeat)
    return throw


# 类型单次（闭包传值）
def cthrow(closure, repeat=None):
    c = Closure(closure)

    def throw(generics):
        return Throw(c)(generics, repeat)
    return throw


# 模块单次
def mthrow(repeat=None):
    m = module(ios=2)

    def throw(generics):
        return Throw(m)(generics, repeat)
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
