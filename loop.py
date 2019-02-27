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
        self.__actions = []
        self.__count = itertools.count(1)
        self.__event = threading.Event()
        self.__shutdown = False
        bregister(self._shutdown)

    # 开始
    @ilock()
    def enter(self, delay, action, args=(), kwargs={}, tag='', log=loge):
        until = time.monotonic() + max(delay, 0)
        eid = next(self.__count)
        if not self.__actions or until < self.__actions[0]['until']:
            self.__event.set()
        self.__actions.append({
            'eid': eid,
            'until': until,
            'action': action,
            'args': args,
            'kwargs': kwargs,
            'tag': tag,
            'log': log,
        })
        self.__actions.sort(key=lambda d: d['until'])
        if not self.is_alive():
            self.start()
        return eid

    # 取消
    @ilock()
    def cancel(self, generics):
        ret = 0
        for i in range(len(self.__actions) - 1, -1, -1):
            p = False
            if generics is None:
                p = True
            elif callable(generics):
                p = self.__actions[i]['action'] is generics
            elif isinstance(generics, int):
                p = self.__actions[i]['eid'] == generics
            elif isinstance(generics, str):
                p = self.__actions[i]['tag'] == generics
            if p:
                self.__actions.pop(i)
                ret += 1
        return ret

    @ilock()
    def _shutdown(self):
        self.__shutdown = True
        self.__event.set()

    def run(self):
        while True:
            pop = None
            timeout = None
            with Lock(self):
                if self.__actions:
                    timeout = self.__actions[0]['until'] - time.monotonic()
                    if timeout <= 0:
                        pop = self.__actions.pop(0)
                elif self.__shutdown:
                    break
                if pop is None:
                    self.__event.clear()
            if pop is not None:
                try:
                    pop['action'](*pop['args'], **pop['kwargs'])
                except BaseException as e:
                    try:
                        callable(pop['log']) and pop['log'](e)
                    except BaseException:
                        pass
            else:
                self.__event.wait(timeout=timeout)


main_loop = Loop()  # 主循环


# 开始
def enter(*args, **kwargs):
    return main_loop.enter(*args, **kwargs)


# 取消
def cancel(*args, **kwargs):
    return main_loop.cancel(*args, **kwargs)
