#!/usr/local/bin/python3
# coding:utf-8
import threading
LOCK = threading.Lock()


# 加锁同步函数
def synchronized():
    def decorator(function):
        name = '__lock__'

        def wrapper(self, *args, **kwargs):
            lock = getattr(self, name, None)
            if not lock:
                LOCK.acquire()
                lock = getattr(self, name, None)
                if not lock:
                    lock = threading.Lock()
                    setattr(self, name, lock)
                LOCK.release()
            lock.acquire()
            ret = function(self, *args, **kwargs)
            lock.release()
            return ret
        return wrapper
    return decorator


# 单次调用函数
def once(crash=False):
    def decorator(function):
        name = function.__qualname__

        def wrapper(self, *args, **kwargs):
            ret = None
            if not getattr(self, name, False):
                setattr(self, name, True)
                ret = function(self, *args, **kwargs)
            elif crash:
                raise Exception('this method can only be used once.')
            return ret
        return wrapper
    return decorator
