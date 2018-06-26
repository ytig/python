#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import classOf, Lock, LOCK_CLASS, synchronized, disposable
from log import Log
TAG = 'task'


class Task:
    def __init__(self, handle, target):
        self.__handle = handle
        self.__target = target
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
        except BaseException as e:
            Log.e(e, tag=TAG)
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
    @disposable()
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
    def __init__(self, handle, *targets):
        self.tasks = [Task(handle, target) for target in targets]

    # 批量执行任务
    def execute(self, t=1):
        return _Executor(*self.tasks).execute(t)


class Queue:
    class Mutex:
        MUTEXS = {}  # 互斥

        @staticmethod
        @synchronized(LOCK_CLASS)
        def instance(key):
            if key not in Queue.Mutex.MUTEXS:
                Queue.Mutex.MUTEXS[key] = Queue.Mutex()
            return Queue.Mutex.MUTEXS[key]

        def __init__(self):
            self.queues = []
            self.running = 0

    # 分派任务
    def push(self):
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
                                Log.e(e, tag=TAG)
                Thread().start()

    # 执行任务
    def pop(self):
        raise NotImplementedError()
