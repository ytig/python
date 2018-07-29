#!/usr/local/bin/python3
import threading
_LOCK = threading.Lock()  # 全局锁
_EVENT_TYPE_BEFORE_SHUTDOWN = 'b'  # 关闭前
_EVENT_TYPE_AFTER_SHUTDOWN = 'a'  # 关闭后
if threading.current_thread() is not threading.main_thread():
    raise Exception('cannot import at thread.')
if threading.main_thread().is_alive():
    _events = []

    def decorator(function):
        def wrapper():
            with _LOCK:
                global _events
                events = _events.copy()
                _events = None
            for type, func, args, kwargs, in events:
                if type == _EVENT_TYPE_BEFORE_SHUTDOWN:
                    try:
                        func(*args, **kwargs)
                    except BaseException:
                        pass
            ret = function()
            for type, func, args, kwargs, in events:
                if type == _EVENT_TYPE_AFTER_SHUTDOWN:
                    try:
                        func(*args, **kwargs)
                    except BaseException:
                        pass
            return ret
        return wrapper
    threading._shutdown = decorator(threading._shutdown)
    del decorator
else:
    _events = None


# 注册（关闭前）
def bregister(*args, **kwargs):
    if len(args) <= 0:
        raise Exception('no func.')
    func = args[0]
    args = args[1:]
    with _LOCK:
        if isinstance(_events, list):
            _events.append((_EVENT_TYPE_BEFORE_SHUTDOWN, func, args, kwargs,))
            return
    try:
        func(*args, **kwargs)
    except BaseException:
        pass


# 注册（关闭后）
def aregister(*args, **kwargs):
    if len(args) <= 0:
        raise Exception('no func.')
    func = args[0]
    args = args[1:]
    with _LOCK:
        if isinstance(_events, list):
            _events.append((_EVENT_TYPE_AFTER_SHUTDOWN, func, args, kwargs,))
            return
    try:
        func(*args, **kwargs)
    except BaseException:
        pass


# 注销
def unregister(func):
    with _LOCK:
        r = 0
        if isinstance(_events, list):
            i = len(_events) - 1
            while i >= 0:
                if _events[i][1] is func:
                    _events.pop(i)
                    r += 1
                i -= 1
        return r
