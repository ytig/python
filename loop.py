#!/usr/local/bin/python3
import time
import threading
import itertools
from decorator import Lock, ilock, ithrow
from ab import weakmethod
from shutdown import bregister, unregister
from logger import loge


class Loop:
    def __init__(self):
        self.targets = []
        self.count = itertools.count(1)
        self.wait = threading.Event()
        self.opened = threading.Event()
        self.closer = threading.Event()
        self.closed = threading.Event()

    # 执行
    @ilock()
    def post(self, target, args=(), kwargs={}, log=loge, delay=0, tag=''):
        assert not self.closed.is_set(), 'loop has been closed'
        until = time.monotonic() + max(delay, 0)
        pid = next(self.count)
        if not self.targets or until < self.targets[0]['until']:
            self.wait.set()
        self.targets.append({
            'until': until,
            'pid': pid,
            'tag': tag,
            'target': target,
            'args': args,
            'kwargs': kwargs,
            'log': log,
        })
        self.targets.sort(key=lambda d: (d['until'], d['pid'],))
        return pid

    # 移除
    @ilock()
    def remove(self, generics):
        ret = 0
        for i in range(len(self.targets) - 1, -1, -1):
            p = False
            if generics is None:
                p = True
            elif isinstance(generics, int):
                p = self.targets[i]['pid'] == generics
            elif isinstance(generics, str):
                p = self.targets[i]['tag'] == generics
            elif callable(generics):
                p = self.targets[i]['target'] is generics
            if p:
                self.targets.pop(i)
                ret += 1
        return ret

    # 开始
    def enter(self):
        with Lock(self):
            assert not self.opened.is_set(), 'loop has been opened'
            self.opened.set()
        while True:
            pop = None
            timeout = None
            with Lock(self):
                if self.targets:
                    timeout = self.targets[0]['until'] - time.monotonic()
                    if timeout <= 0:
                        pop = self.targets.pop(0)
                elif self.closer.is_set():
                    self.closed.set()
                    break
                if pop is None:
                    self.wait.clear()
            if pop is not None:
                try:
                    pop['target'](*pop['args'], **pop['kwargs'])
                except BaseException as e:
                    try:
                        callable(pop['log']) and pop['log'](e)
                    except BaseException:
                        pass
            else:
                self.wait.wait(timeout=timeout)

    # 退出
    def exit(self):
        with Lock(self):
            self.closer.set()
            if not self.opened.is_set() and not self.targets:
                self.closed.set()
        self.wait.set()


class LoopThread(threading.Thread):
    def __init__(self, daemon=None):
        super().__init__(daemon=daemon)
        self.loop = Loop()
        self.__shutdown__ = weakmethod(self, 'shutdown')
        bregister(self.__shutdown__)

    # 执行
    def post(self, *args, **kwargs):
        pid = self.loop.post(*args, **kwargs)
        self.start()
        return pid

    # 移除
    def remove(self, *args, **kwargs):
        return self.loop.remove(*args, **kwargs)

    # 终止
    def shutdown(self):
        unregister(self.__shutdown__)
        self.loop.exit()

    @ilock()
    @ithrow()
    def start(self):
        return super().start()

    def run(self):
        self.loop.enter()
