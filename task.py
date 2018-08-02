#!/usr/local/bin/python3
import threading
from kit import hasvar, getvar, setvar, loge
from decorator import Lock, ilock, ithrow, instance


def Pair(function):
    def wrapper(*args, **kwargs):
        threading.Thread(target=function, args=args, kwargs=kwargs).start()
    return wrapper


class Queue:
    # 打印日志
    @staticmethod
    def log(e):
        logging.Log.e(loge(e))

    @classmethod
    def __run(cls):
        name = '__mutex__'
        while True:
            with Lock(cls):
                mutex = getvar(cls, name)
                if mutex['q']:
                    queue = mutex['q'].pop(0)
                else:
                    mutex['r'] -= 1
                    break
            try:
                queue.pop()
            except BaseException as e:
                try:
                    getattr(cls, 'log')(e)
                except BaseException:
                    pass

    # 任务分发
    def push(self):
        cls = self.__class__
        name = '__mutex__'
        with Lock(cls):
            assert hasvar(cls, name) or setvar(cls, name, {'q': [], 'r': 0, })
            mutex = getvar(cls, name)
            mutex['q'].append(self)
            if mutex['r'] < 1:
                threading.Thread(target=cls.__run).start()
                mutex['r'] += 1

    # 任务处理
    def pop(self):
        pass


class Tree:
    class Twig:
        def __init__(self, cpu, mem, log):
            self.__cpu = cpu
            self.__mem = mem
            self.__log = log
            self.__ret = (False, None,)

        @ilock()
        def plant(self):
            try:
                if not self.__ret[0]:
                    self.__ret = (True, self.__cpu(self.__mem),)
            except BaseException as e:
                try:
                    self.__log(e)
                except BaseException:
                    pass
            return self.__ret

    class Gardener:
        class Executor(threading.Thread):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue

            def run(self):
                while True:
                    twig = self.queue.pop()
                    if twig is None:
                        break
                    ret = twig.plant()
                    if ret[0]:
                        self.queue.push(ret[1])

        def __init__(self, *twigs):
            self.twigs = list(twigs)
            self.seeds = []

        @ilock()
        def pop(self):
            if self.twigs:
                return self.twigs.pop()
            return None

        @ilock()
        def push(self, seed):
            self.seeds.append(seed)

        @ithrow()
        def plant(self, t):
            threads = [Tree.Gardener.Executor(self) for i in range(t)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            return self.seeds

    def __init__(self, cpu, *mems, log=lambda e: logging.Log.e(loge(e))):
        self.twigs = [Tree.Twig(cpu, mem, log) for mem in mems]

    # 任务并发
    def plant(self, t=1):
        return Tree.Gardener(*self.twigs).plant(t)


import log as logging
