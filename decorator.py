#!/usr/local/bin/python3
# coding:utf-8
import inspect
import threading
_LOCK = threading.Lock()  # 全局锁
_MODULES = {}  # 伪模块
_CLASSES = {}  # 伪类型


# 获取伪模块
def moduleOf(generics):
    if isinstance(generics, str):
        with _LOCK:
            if generics not in _MODULES:
                _MODULES[generics] = lambda: generics
            return _MODULES[generics]
    else:
        return moduleOf(inspect.getmodule(generics).__name__)


# 获取伪类型
def classOf(generics):
    if isinstance(generics, str):
        with _LOCK:
            if generics not in _CLASSES:
                _CLASSES[generics] = lambda: generics
            return _CLASSES[generics]
    elif inspect.ismodule(generics):
        return classOf(generics.__name__)
    elif inspect.isclass(generics):
        return classOf(generics.__module__ + '.' + generics.__qualname__)
    elif inspect.isfunction(generics) or inspect.ismethod(generics):
        return classOf(generics.__module__ + '.' + generics.__qualname__.rsplit('.', 1)[0])
    else:
        return classOf(generics.__class__)


class Lock:
    def __init__(self, object):
        self.object = object

    @staticmethod
    def __lockOf(object):
        if inspect.ismodule(object):
            name = '__LOCK__'
        elif inspect.isclass(object):
            name = '__Lock__'
        else:
            name = '__lock__'
        if not hasattr(object, name):
            setattr(object, name, (threading.Lock(), [],))
        return getattr(object, name)

    def __enter__(self):
        if self.object is not None:
            tn = threading.current_thread().name
            with _LOCK:
                lock, stack = Lock.__lockOf(self.object)
                a = tn not in stack
                if not a:
                    stack.append(tn)
            if a:
                lock.acquire()
                with _LOCK:
                    stack.append(tn)

    def __exit__(self, type, value, traceback):
        if self.object is not None:
            with _LOCK:
                lock, stack = Lock.__lockOf(self.object)
                stack.pop()
                r = len(stack) == 0
            if r:
                lock.release()


LOCK_INSTANCE = 0b1  # 实例锁
LOCK_CLASS = 0b10  # 类型锁
LOCK_MODULE = 0b100  # 模块锁


# 加锁同步函数
def synchronized(lock=LOCK_INSTANCE):
    i = True if lock & LOCK_INSTANCE else False
    c = True if lock & LOCK_CLASS else False
    m = True if lock & LOCK_MODULE else False

    def decorator(function):
        lm = Lock(moduleOf(function) if m else None)
        lc = Lock(classOf(function) if c else None)

        def wrapper(*args, **kwargs):
            if i and len(args) <= 0:
                raise Exception('no self.')
            li = Lock(args[0] if i else None)
            with lm:
                with lc:
                    with li:
                        return function(*args, **kwargs)
        return wrapper
    return decorator


# 单次调用函数
def disposable(static=False, repeat=None):
    if isinstance(repeat, str):
        def call(function, object, name, *args, **kwargs):
            if not getattr(object, name, False):
                kwargs.update({repeat: False, })
                try:
                    r = function(*args, **kwargs)
                except BaseException as e:
                    raise e
                else:
                    setattr(object, name, True)
                    return r
            else:
                kwargs.update({repeat: True, })
                return function(*args, **kwargs)
    else:
        if not callable(repeat):
            repeat = lambda *args, **kwargs: None

        def call(function, object, name, *args, **kwargs):
            if not getattr(object, name, False):
                try:
                    r = function(*args, **kwargs)
                except BaseException as e:
                    raise e
                else:
                    setattr(object, name, True)
                return r
            else:
                return repeat(*args, **kwargs)

    def decorator(function):
        name = function.__qualname__
        if static:
            module = moduleOf(function)

        def wrapper(*args, **kwargs):
            if static:
                object = module
            else:
                if len(args) <= 0:
                    raise Exception('no self.')
                object = args[0]
            return call(function, object, name, *args, **kwargs)
        return wrapper
    return decorator
