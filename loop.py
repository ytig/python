#!/usr/local/bin/python3
import time
import threading
import itertools
from decorator import Lock, ilock
from ab import weakmethod
from shutdown import bregister, unregister
from logger import loge


class Loop(threading.Thread):
    def __init__(self, daemon=False):
        super().__init__(daemon=daemon)
        self._targets = []
        self._count = itertools.count(1)
        self._wait = threading.Event()
        self._closer = threading.Event()
        self._closed = threading.Event()
        self.__shutdown__ = weakmethod(self, 'shutdown')
        bregister(self.__shutdown__)

    # 执行
    @ilock()
    def post(self, target, args=(), kwargs={}, log=loge, delay=0, tag=''):
        until = time.monotonic() + max(delay, 0)
        pid = next(self._count)
        if not self._targets or until < self._targets[0]['until']:
            self._wait.set()
        self._targets.append({
            'until': until,
            'pid': pid,
            'tag': tag,
            'target': target,
            'args': args,
            'kwargs': kwargs,
            'log': log,
        })
        self._targets.sort(key=lambda d: (d['until'], d['pid'],))
        if not self.is_alive():
            self.start()
        return pid

    # 移除
    @ilock()
    def remove(self, generics):
        ret = 0
        for i in range(len(self._targets) - 1, -1, -1):
            p = False
            if generics is None:
                p = True
            elif isinstance(generics, int):
                p = self._targets[i]['pid'] == generics
            elif isinstance(generics, str):
                p = self._targets[i]['tag'] == generics
            elif callable(generics):
                p = self._targets[i]['target'] is generics
            if p:
                self._targets.pop(i)
                ret += 1
        return ret

    # 终止
    def shutdown(self):
        unregister(self.__shutdown__)
        self._closer.set()
        self._wait.set()
        self._closed.wait()

    def run(self):
        while True:
            pop = None
            timeout = None
            with Lock(self):
                if self._targets:
                    timeout = self._targets[0]['until'] - time.monotonic()
                    if timeout <= 0:
                        pop = self._targets.pop(0)
                elif self._closer.is_set():
                    break
                if pop is None:
                    self._wait.clear()
            if pop is not None:
                try:
                    pop['target'](*pop['args'], **pop['kwargs'])
                except BaseException as e:
                    try:
                        callable(pop['log']) and pop['log'](e)
                    except BaseException:
                        pass
            else:
                self._wait.wait(timeout=timeout)
        self._closed.set()


main_loop = Loop()  # 主循环


# 执行
def post(*args, **kwargs):
    return main_loop.post(*args, **kwargs)


# 移除
def remove(*args, **kwargs):
    return main_loop.remove(*args, **kwargs)
