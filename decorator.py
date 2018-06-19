#!/usr/local/bin/python3
# coding:utf-8
import inspect
import threading
_LOCK = threading.Lock()  # 全局锁
_CLASSES = {}  # 伪类


# 获取伪类
def classOf(function):
    className = inspect.getmodule(function).__name__ + '.' + function.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
    with _LOCK:
        if className not in _CLASSES:
            _CLASSES[className] = lambda: None
        return _CLASSES[className]


class Lock:
    def __init__(self, object):
        self.object = object
        self.name = '__LOCK__' if inspect.isclass(object) else '__lock__'

    def __enter__(self):
        tn = threading.current_thread().name
        with _LOCK:
            if not hasattr(self.object, self.name):
                setattr(self.object, self.name, (threading.Lock(), [],))
            lock, stack = getattr(self.object, self.name)
            a = tn not in stack
            if not a:
                stack.append(tn)
        if a:
            lock.acquire()
            with _LOCK:
                stack.append(tn)

    def __exit__(self, type, value, traceback):
        with _LOCK:
            lock, stack = getattr(self.object, self.name)
            stack.pop()
            r = len(stack) == 0
        if r:
            lock.release()


LOCK_CLASS = 0b1  # 类锁
LOCK_INSTANCE = 0b10  # 实例锁


# 加锁同步函数
def synchronized(lock=LOCK_INSTANCE):
    lc = True if lock & LOCK_CLASS else False
    li = True if lock & LOCK_INSTANCE else False

    def decorator(function):
        cls = classOf(function)
        if li:
            if lc:
                def wrapper(self, *args, **kwargs):
                    with Lock(cls):
                        with Lock(self):
                            return function(self, *args, **kwargs)
            else:
                def wrapper(self, *args, **kwargs):
                    with Lock(self):
                        return function(self, *args, **kwargs)
        else:
            if lc:
                def wrapper(*args, **kwargs):
                    with Lock(cls):
                        return function(*args, **kwargs)
            else:
                def wrapper(*args, **kwargs):
                    return function(*args, **kwargs)
        return wrapper
    return decorator


# 单次调用函数
def disposable(static=False, crash=False):
    def decorator(function):
        name = function.__qualname__
        if not static:
            def wrapper(self, *args, **kwargs):
                ret = None
                if not getattr(self, name, False):
                    try:
                        ret = function(self, *args, **kwargs)
                    except BaseException as e:
                        raise e
                    else:
                        setattr(self, name, True)
                elif crash:
                    raise Exception('this method can only be used once.')
                return ret
        else:
            cls = classOf(function)

            def wrapper(*args, **kwargs):
                ret = None
                if not getattr(cls, name, False):
                    try:
                        ret = function(*args, **kwargs)
                    except BaseException as e:
                        raise e
                    else:
                        setattr(cls, name, True)
                elif crash:
                    raise Exception('this function can only be used once.')
                return ret
        return wrapper
    return decorator
