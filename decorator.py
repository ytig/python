#!/usr/local/bin/python3
import json
import inspect
import threading
import atexit
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
        self.stack = list()

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

    # 区块锁
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
            if generics.__func__:
                return staticmethod(decorator(generics.__func__))
            else:
                return generics
        elif isinstance(generics, classmethod):
            if generics.__func__:
                return classmethod(decorator(generics.__func__))
            else:
                return generics
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
    i = Closure(lambda: frames(back=4)[0].f_locals['args'][0])

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
    m = module(back=1)

    def lock(generics):
        return Lock(m, k=k)(generics)
    return lock


class Throw:
    def __init__(self, generics):
        self.generics = generics
        self.stack = list()

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

    # 区块单次（代码）
    def __enter__(self):
        with frames(back=1) as f:
            assert f.has(0)
            xid = 'X:' + f[0].f_code.co_filename + '/' + str(f[0].f_lineno)
        self.stack.append(xid)
        return xid in self.__throw

    def __exit__(self, t, v, tb):
        xid = self.stack.pop()
        if t is None:
            self.__throw.add(xid)

    # 装饰单次（实例）
    def __call__(self, generics, r=None):
        def decorator(call):
            sid = 'S:' + unique()
            if isinstance(r, str):
                a = bind(call, **{r: False, })
                b = bind(call, **{r: True, })
            else:
                a = call
                b = r if callable(r) else lambda *args, **kwargs: None

            def wrapper(*args, **kwargs):
                throw = self.__throw
                if sid not in throw:
                    ret = a(*args, **kwargs)
                    throw.add(sid)
                    return ret
                else:
                    return b(*args, **kwargs)
            return wrapper
        if callable(generics):
            return decorator(generics)
        elif isinstance(generics, staticmethod):
            if generics.__func__:
                return staticmethod(decorator(generics.__func__))
            else:
                return generics
        elif isinstance(generics, classmethod):
            if generics.__func__:
                return classmethod(decorator(generics.__func__))
            else:
                return generics
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
    i = Closure(lambda: frames(back=3)[0].f_locals['args'][0])

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
    m = module(back=1)

    def throw(generics):
        return Throw(m)(generics, r=r)
    return throw


# 单例类型（同参）
def instance():
    def decorator(__class__):
        cid = unique()
        none = object()

        def init(ret=getvar(__class__, '__init__', d=none)):
            if ret is none:
                for b in type.mro(__class__)[1:]:
                    if b is object:
                        ret = lambda self, *args, **kwargs: object.__dict__['__init__'](self, *args, **kwargs)
                        break
                    elif hasvar(b, '__init__'):
                        ret = getvar(b, '__init__')
                        break
            assert callable(ret)
            return ret

        def __init__(self, *args, **kwargs):
            if type(self) is __class__:
                with Lock(self):
                    with Lock(instance):
                        instances = getvar(instance, '__instance__')[cid]
                        assert self in instances.values()
                    try:
                        assert hasvar(self, '__old__') or setvar(self, '__old__', init()(self, *args, **kwargs))
                        return getvar(self, '__old__')
                    except BaseException:
                        with Lock(instance):
                            for k in tuple(instances.keys()):
                                if instances[k] is self:
                                    del instances[k]
                        raise
            else:
                return init()(self, *args, **kwargs)
        assert setvar(__class__, '__init__', __init__)

        def new(ret=getvar(__class__, '__new__', d=none)):
            if ret is none:
                for b in type.mro(__class__)[1:]:
                    if b is object:
                        ret = staticmethod(lambda *args, **kwargs: object.__dict__['__new__'](args[0]))
                        break
                    elif hasvar(b, '__new__'):
                        ret = getvar(b, '__new__')
                        break
            assert isinstance(ret, staticmethod) and callable(ret.__func__)
            return ret.__func__

        @staticmethod
        def __new__(*args, **kwargs):
            if args[0] is __class__:
                sid = json.dumps((args[1:], sorted(kwargs.items(), key=lambda i: i[0]),))
                with Lock(instance):
                    assert hasvar(instance, '__instance__') or setvar(instance, '__instance__', dict())
                    INSTANCES = getvar(instance, '__instance__')
                    if cid not in INSTANCES:
                        INSTANCES[cid] = dict()
                    instances = INSTANCES[cid]
                    if sid not in instances:
                        instances[sid] = new()(*args, **kwargs)
                    return instances[sid]
            else:
                return new()(*args, **kwargs)
        assert setvar(__class__, '__new__', __new__)
        return __class__
    return decorator


atexit.register(lambda: setvar(instance, '__instance__', None))
