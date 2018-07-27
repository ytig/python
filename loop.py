#!/usr/local/bin/python3
import time
import threading
import subprocess
from decorator import Lock
from log import Log
TAG = __name__


class Loop(threading.Thread):
    def __init__(self, daemon=False):
        super().__init__(daemon=daemon)
        self.__pid = 0
        self.__pool = []
        self.__process = None

    # 执行
    def do(self, runnable, delay, tag='', log=lambda e: Log.e(e, tag=TAG)):
        if not isinstance(tag, str):
            raise Exception('tag must be str.')
        t = time.time() + delay
        with Lock(self):
            self.__pid += 1
            pid = self.__pid
            if not self.__pool or t < self.__pool[0][0]:
                if self.__process is not None:
                    try:
                        self.__process.kill()
                    except BaseException:
                        pass
                    self.__process = None
            self.__pool.append((t, runnable, pid, tag, log,))
            self.__pool.sort(key=lambda t: t[0])
        if not self.is_alive():
            self.start()
        return pid

    # 取消执行
    def undo(self, generics):
        r = 0
        with Lock(self):
            i = len(self.__pool) - 1
            while i >= 0:
                p = False
                if generics is None:
                    p = True
                elif callable(generics):
                    p = self.__pool[i][1] is generics
                elif isinstance(generics, int):
                    p = self.__pool[i][2] == generics
                elif isinstance(generics, str):
                    p = self.__pool[i][3] == generics
                if p:
                    self.__pool.pop(i)
                    if i == 0:
                        if self.__process is not None:
                            try:
                                self.__process.kill()
                            except BaseException:
                                pass
                            self.__process = None
                    r += 1
                i -= 1
        return r

    def run(self):
        while True:
            process = None
            pop = None
            with Lock(self):
                self.__process = None
                if self.__pool:
                    t = self.__pool[0][0] - time.time()
                else:
                    if not self.daemon:
                        if not threading.main_thread().is_alive():
                            return
                        t = 2
                    else:
                        t = 24
                if t > 0:
                    process = subprocess.Popen(['sleep', str(t)])
                    self.__process = process
                else:
                    pop = self.__pool.pop(0)
            if process is not None:
                try:
                    process.wait()
                except BaseException:
                    pass
            if pop is not None:
                try:
                    pop[1]()
                except BaseException as e:
                    try:
                        pop[-1](e)
                    except BaseException:
                        pass


main_loop = Loop()  # 主循环


# 执行
def do(runnable, delay, tag=''):
    return main_loop.do(runnable, delay, tag=tag)


# 取消执行
def undo(generics):
    return main_loop.undo(generics)
