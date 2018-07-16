#!/usr/local/bin/python3
import threading
from decorator import classOf, Lock, synchronized, throwaway, instance
TAG = __name__


def Pair(function):
    def wrapper(*args, **kwargs):
        threading.Thread(target=function, args=args, kwargs=kwargs).start()
    return wrapper


class Queue:
    @instance()
    class Mutex:
        def __init__(self, cn):
            self.queues = []
            self.running = 0

    class Executor(threading.Thread):
        def __init__(self, mutex):
            super().__init__()
            self.mutex = mutex

        def run(self):
            while True:
                with Lock(self.mutex):
                    if self.mutex.queues:
                        queue = self.mutex.queues.pop(0)
                    else:
                        self.mutex.running -= 1
                        break
                try:
                    queue.pop()
                except BaseException as e:
                    try:
                        getattr(queue.__class__, 'log', None)(e)
                    except BaseException:
                        pass

    # 打印日志
    @staticmethod
    def log(e):
        log.Log.e(e, tag=TAG)

    # 任务分发
    def push(self):
        mutex = Queue.Mutex.instanceOf(classOf(self)())
        with Lock(mutex):
            mutex.queues.append(self)
            if mutex.running < 1:
                mutex.running += 1
                Queue.Executor(mutex).start()

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

        @synchronized()
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

        @synchronized()
        def pop(self):
            if self.twigs:
                return self.twigs.pop()
            return None

        @synchronized()
        def push(self, seed):
            self.seeds.append(seed)

        @throwaway()
        def plant(self, t):
            threads = [Tree.Gardener.Executor(self) for i in range(t)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            return self.seeds

    def __init__(self, cpu, *mems, log=lambda e: log.Log.e(e, tag=TAG)):
        self.twigs = [Tree.Twig(cpu, mem, log) for mem in mems]

    # 任务并发
    def plant(self, t=1):
        return Tree.Gardener(*self.twigs).plant(t)


import log
