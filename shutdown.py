#!/usr/local/bin/python3
import threading
from decorator import LOCK_MODULE, synchronized, throwaway
_events = []  # 事件


# 注册
@synchronized(lock=LOCK_MODULE)
def register(*args, **kwargs):
    if len(args) <= 0:
        raise Exception('no func.')
    func = args[0]
    args = args[1:]
    if isinstance(_events, list):
        _events.append((func, args, kwargs,))
        _hook()
        return True
    else:
        return False


# 注销
@synchronized(lock=LOCK_MODULE)
def unregister(func):
    r = 0
    if isinstance(_events, list):
        i = len(_events) - 1
        while i >= 0:
            if _events[i][0] is func:
                _events.pop(i)
                r += 1
            i -= 1
    return r


@synchronized(lock=LOCK_MODULE)
def _shutdown():
    global _events
    while _events:
        func, args, kwargs = _events.pop()
        func(*args, **kwargs)
    _events = None


@throwaway(static=True)
def _hook():
    if threading.main_thread().is_alive():
        def decorator(function):
            def wrapper():
                _shutdown()
                return function()
            return wrapper
        threading._shutdown = decorator(threading._shutdown)
    else:
        _shutdown()
