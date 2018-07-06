#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import classOf, Lock, synchronized, throwaway, instance
TAG = __name__


class Task:
    def __init__(self, handle, target, log=lambda e: log.Log.e(e, tag=TAG)):
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


class Tasks:
    class Executor:
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

    def __init__(self, handle, *targets, **kwargs):
        self.tasks = [Task(handle, target, **kwargs) for target in targets]

    # 批量执行任务
    def execute(self, t=1):
        return Tasks.Executor(*self.tasks).execute(t)


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

    # 分派任务
    def push(self):
        mutex = Queue.Mutex.instanceOf(classOf(self)())
        with Lock(mutex):
            mutex.queues.append(self)
            if mutex.running < 1:
                mutex.running += 1
                Queue.Executor(mutex).start()

    # 执行任务
    def pop(self):
        pass


import log
