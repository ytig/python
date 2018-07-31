#!/usr/local/bin/python3
import threading
_LOCK = threading.Lock()  # 全局锁
if threading.current_thread() is not threading.main_thread():
    raise Exception('cannot import at thread.')
if threading.main_thread().is_alive():
    _current_state = 0
    _events = []

    def decorator(function):
        def step():
            global _current_state
            events = []
            with _LOCK:
                _current_state += 1
                for i in range(len(_events) - 1, -1, -1):
                    if _current_state >= _events[i][0]:
                        events.append(_events.pop(i))
            for type, func, args, kwargs, in events:
                try:
                    func(*args, **kwargs)
                except BaseException:
                    pass

        def wrapper():
            step()
            ret = function()
            step()
            return ret
        return wrapper
    threading._shutdown = decorator(threading._shutdown)
    del decorator
else:
    _current_state = -1
    _events = []


# 注册（关闭前）
def bregister(*args, **kwargs):
    if len(args) <= 0:
        raise Exception('no func.')
    func = args[0]
    args = args[1:]
    with _LOCK:
        if _current_state in range(1):
            _events.append((1, func, args, kwargs,))
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
        if _current_state in range(2):
            _events.append((2, func, args, kwargs,))
            return
    try:
        func(*args, **kwargs)
    except BaseException:
        pass


# 注销
def unregister(func):
    with _LOCK:
        r = 0
        for i in range(len(_events) - 1, -1, -1):
            if _events[i][1] is func:
                _events.pop(i)
                r += 1
        return r
