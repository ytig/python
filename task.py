#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import synchronized
from log import Log
TAG = 'task'


class Task:
    def __init__(self, handler, target):
        self.handler = handler
        self.target = target
        self.result = None

    # 处理任务
    def handle(self):
        try:
            self.handler(self.target)
        except BaseException as e:
            self.result = False
            Log.e(e, tag=TAG)
        else:
            self.result = True


class Tasks:
    def __init__(self, handler, *targets):
        self.tasks = [Task(handler, target) for target in targets]

    # 批量处理任务
    def handle(self, t=1):
        self.__reset()
        pop = self.__pop

        class Thread(threading.Thread):
            def run(self):
                while True:
                    task = pop()
                    if task is None:
                        break
                    task.handle()
        threads = [Thread() for i in range(t)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return [task.result for task in self.tasks].count(True)

    def __reset(self):
        self.__tasks = []
        for task in self.tasks:
            if not task.result:
                self.__tasks.append(task)

    @synchronized()
    def __pop(self):
        if self.__tasks:
            return self.__tasks.pop()
        return None
