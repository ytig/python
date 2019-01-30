#!/usr/local/bin/python3
import time
import threading
import itertools
import subprocess
from kit import loge
from decorator import Lock
from shutdown import bregister
from logger import Log


# 睡眠进程
def sleep(seconds):
    if seconds < 0:
        return subprocess.Popen(['sleep', '224', ])
    else:
        return subprocess.Popen(['sleep', '%s' % (seconds,), ])


class Loop(threading.Thread):
    def __init__(self, daemon=False):
        super().__init__(daemon=daemon)
        self.__count = itertools.count(1)
        self.__actions = []
        self.__process = None
        self.__shutdown = False
        bregister(self._shutdown)

    # 开始
    def enter(self, delay, action, args=(), kwargs={}, tag='', log=lambda e: Log.e(loge(e))):
        until = time.time() + max(0, delay)
        with Lock(self):
            eid = next(self.__count)
            if not self.__actions or until < self.__actions[0]['until']:
                if self.__process is not None:
                    try:
                        self.__process.kill()
                    except BaseException:
                        pass
                    self.__process = None
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
    def cancel(self, generics):
        ret = 0
        with Lock(self):
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
                    if i == 0:
                        if self.__process is not None:
                            try:
                                self.__process.kill()
                            except BaseException:
                                pass
                            self.__process = None
                    ret += 1
        return ret

    def _shutdown(self):
        with Lock(self):
            self.__shutdown = True
            if self.__process is not None:
                try:
                    self.__process.kill()
                except BaseException:
                    pass
                self.__process = None

    def run(self):
        while True:
            process = None
            pop = None
            with Lock(self):
                self.__process = None
                if self.__actions:
                    t = self.__actions[0]['until'] - time.time()
                    t = t if t > 0 else None
                elif self.__shutdown:
                    return
                else:
                    t = -1
                if t is not None:
                    process = sleep(t)
                    self.__process = process
                else:
                    pop = self.__actions.pop(0)
            if process is not None:
                try:
                    process.wait()
                except BaseException:
                    pass
            if pop is not None:
                try:
                    pop['action'](*pop['args'], **pop['kwargs'])
                except BaseException as e:
                    try:
                        callable(pop['log']) and pop['log'](e)
                    except BaseException:
                        pass


main_loop = Loop()  # 主循环


# 开始
def enter(*args, **kwargs):
    return main_loop.enter(*args, **kwargs)


# 取消
def cancel(*args, **kwargs):
    return main_loop.cancel(*args, **kwargs)
