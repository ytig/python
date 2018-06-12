#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import synchronized
from log import Log
TAG = 'task'


class Task:
    def __init__(self, handle, target):
        self.handle = handle
        self.target = target
        self.result = None

    # 执行任务
    def execute(self):
        try:
            self.handle(self.target)
        except BaseException as e:
            Log.e(e, tag=TAG)
            self.result = False
        else:
            self.result = True
        return self.result


class Tasks:
    def __init__(self, handle, *targets):
        self.tasks = [Task(handle, target) for target in targets]

    def __push(self):
        self.__tasks = []
        for task in self.tasks:
            if not task.result:
                self.__tasks.append(task)

    @synchronized()
    def __pop(self):
        if self.__tasks:
            return self.__tasks.pop()
        return None

    # 批量执行任务
    def execute(self, t=1):
        self.__push()
        pop = self.__pop

        class Thread(threading.Thread):
            def run(self):
                while True:
                    task = pop()
                    if task is None:
                        break
                    task.execute()
        threads = [Thread() for i in range(t)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return [task.result for task in self.tasks].count(True)
