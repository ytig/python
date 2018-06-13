#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import synchronized
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
