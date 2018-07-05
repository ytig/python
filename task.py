#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import classOf, Lock, LOCK_CLASS, synchronized, throwaway
TAG = 'task'


class Task:
    def __init__(self, handle, target, log=lambda e: __import__('log').Log.e(e, tag=TAG)):
        self.__handle = handle
        self.__target = target
        self.__log = log
        self.result = False

    # 执行任务
    @synchronized()
    def execute(self):
        try:
            if not self.result:
                self.__handle(self.__target)
                self.result = True
                del self.__target
                del self.__handle
                del self.__log
        except BaseException as e:
            try:
                self.__log(e)
            except BaseException:
                pass
        return self.result


class _Executor:
    def __init__(self, *tasks):
        self.tasks = list(tasks)
        self.backs = 0

    @synchronized()
    def pop(self):
        if self.tasks:
            return self.tasks.pop()
        return None

    @synchronized()
    def push(self):
        self.backs += 1

    # 批量执行任务
    @throwaway()
    def execute(self, t):
        e = self

        class Thread(threading.Thread):
            def run(self):
                while True:
                    task = e.pop()
                    if task is None:
                        break
                    if task.execute():
                        e.push()
        threads = [Thread() for i in range(t)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return self.backs


class Tasks:
    def __init__(self, handle, *targets, **kwargs):
        self.tasks = [Task(handle, target, **kwargs) for target in targets]

    # 批量执行任务
    def execute(self, t=1):
        return _Executor(*self.tasks).execute(t)


class Queue:
    class Mutex:
        MUTEXS = {}  # 互斥

        @staticmethod
        @synchronized(lock=LOCK_CLASS)
        def instance(key):
            if key not in Queue.Mutex.MUTEXS:
                Queue.Mutex.MUTEXS[key] = Queue.Mutex()
            return Queue.Mutex.MUTEXS[key]

        def __init__(self):
            self.queues = []
            self.running = 0

    # 打印日志
    @staticmethod
    def log(e):
        __import__('log').Log.e(e, tag=TAG)

    # 分派任务
    def push(self):
        log = getattr(self.__class__, 'log', None)
        mutex = Queue.Mutex.instance(classOf(self)())
        with Lock(mutex):
            mutex.queues.append(self)
            if mutex.running < 1:
                mutex.running += 1

                class Thread(threading.Thread):
                    def run(self):
                        while True:
                            with Lock(mutex):
                                if mutex.queues:
                                    queue = mutex.queues.pop(0)
                                else:
                                    mutex.running -= 1
                                    break
                            try:
                                queue.pop()
                            except BaseException as e:
                                try:
                                    log(e)
                                except BaseException:
                                    pass
                Thread().start()

    # 执行任务
    def pop(self):
        pass
