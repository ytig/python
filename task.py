#!/usr/local/bin/python3
import threading
from kit import hasvar, getvar, setvar, loge
from decorator import Lock, ilock


class Queue:
    # 任务分发
    def push(self):
        cls = type(self)
        with Lock(cls):
            assert hasvar(cls, '__mutex__') or setvar(cls, '__mutex__', {'targets': [], 'running': 0, })
            mutex = getvar(cls, '__mutex__')
            mutex['targets'].append(self)
            if mutex['running'] < 1:
                threading.Thread(target=cls.__run).start()
                mutex['running'] += 1

    # 任务处理
    def pop(self):
        pass

    # 打印日志
    @staticmethod
    def log(e):
        logger.Log.e(loge(e))

    @classmethod
    def __run(cls):
        while True:
            with Lock(cls):
                mutex = getvar(cls, '__mutex__')
                if mutex['targets']:
                    target = mutex['targets'].pop(0)
                else:
                    mutex['running'] -= 1
                    break
            try:
                target.pop()
            except BaseException as e:
                try:
                    cls.log(e)
                except BaseException:
                    pass


class Tree:
    SEIZE = object()  # 占位符

    class Twig:
        def __init__(self, target, args=(), kwargs={}, log=lambda e: logger.Log.e(loge(e))):
            self.target = target
            self.args = args
            self.kwargs = kwargs
            self.log = log
            self.ret = (False, None,)

        @ilock()
        def __call__(self):
            if not self.ret[0]:
                try:
                    self.ret = (True, self.target(*self.args, **self.kwargs),)
                    del self.target, self.args, self.kwargs, self.log,
                except BaseException as e:
                    callable(self.log) and self.log(e)
            return self.ret

    def __init__(self, t):
        self.t = t
        self.targets = []
        self.running = 0

    # 任务并发
    def plant(self, *twigs, seize=False):
        ret = []
        if self.t < 0:
            for twig in twigs:
                b, r, = twig()
                if not b:
                    break
                ret.append(r)
            ret += [Tree.SEIZE, ] * (len(twigs) - len(ret))
        elif self.t == 0:
            for twig in twigs:
                b, r, = twig()
                ret.append(r if b else Tree.SEIZE)
        else:
            with Lock(self):
                targets = [{'twig': twig, 'event': threading.Event(), } for twig in twigs]
                self.targets.extend(targets)
                for i in range(min(len(targets), self.t - self.running)):
                    threading.Thread(target=self.__run).start()
                    self.running += 1
            for target in targets:
                target['event'].wait()
                b, r, = target['ret']
                ret.append(r if b else Tree.SEIZE)
        if not seize:
            while Tree.SEIZE in ret:
                ret.remove(Tree.SEIZE)
        return ret

    def __run(self):
        while True:
            with Lock(self):
                if self.targets:
                    target = self.targets.pop(0)
                else:
                    self.running -= 1
                    break
            target['ret'] = target['twig']()
            target['event'].set()


import logger
