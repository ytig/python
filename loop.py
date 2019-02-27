#!/usr/local/bin/python3
import time
import threading
import itertools
from decorator import Lock, ilock
from shutdown import bregister
from logger import loge


class Loop(threading.Thread):
    def __init__(self, daemon=False):
        super().__init__(daemon=daemon)
        self._actions = []
        self._count = itertools.count(1)
        self._event = threading.Event()
        self._shutdown = False
        bregister(self.shutdown)

    # 开始
    @ilock()
    def enter(self, delay, action, args=(), kwargs={}, tag='', log=loge):
        until = time.monotonic() + max(delay, 0)
        pid = next(self._count)
        if not self._actions or until < self._actions[0]['until']:
            self._event.set()
        self._actions.append({
            'pid': pid,
            'until': until,
            'action': action,
            'args': args,
            'kwargs': kwargs,
            'tag': tag,
            'log': log,
        })
        self._actions.sort(key=lambda d: d['until'])
        if not self.is_alive():
            self.start()
        return pid

    # 取消
    @ilock()
    def cancel(self, generics):
        ret = 0
        for i in range(len(self._actions) - 1, -1, -1):
            p = False
            if generics is None:
                p = True
            elif callable(generics):
                p = self._actions[i]['action'] is generics
            elif isinstance(generics, int):
                p = self._actions[i]['pid'] == generics
            elif isinstance(generics, str):
                p = self._actions[i]['tag'] == generics
            if p:
                self._actions.pop(i)
                ret += 1
        return ret

    @ilock()
    def shutdown(self):
        self._shutdown = True
        self._event.set()

    def run(self):
        while True:
            pop = None
            timeout = None
            with Lock(self):
                if self._actions:
                    timeout = self._actions[0]['until'] - time.monotonic()
                    if timeout <= 0:
                        pop = self._actions.pop(0)
                elif self._shutdown:
                    break
                if pop is None:
                    self._event.clear()
            if pop is not None:
                try:
                    pop['action'](*pop['args'], **pop['kwargs'])
                except BaseException as e:
                    try:
                        callable(pop['log']) and pop['log'](e)
                    except BaseException:
                        pass
            else:
                self._event.wait(timeout=timeout)


main_loop = Loop()  # 主循环


# 开始
def enter(*args, **kwargs):
    return main_loop.enter(*args, **kwargs)


# 取消
def cancel(*args, **kwargs):
    return main_loop.cancel(*args, **kwargs)
