#!/usr/local/bin/python3
import inspect
import threading
from kit import loge
from decorator import Lock, ilock
from logger import Log


# 并发执行
def execute(function, *arguments, t=0):
    if not inspect.getfullargspec(function).args:
        function = lambda _, f=function: f()
    result = Tree(t=t).plant(*[Tree.Twig(function, args=(argument,)) for argument in arguments], seize=True)
    if Tree.SEIZE in result:
        raise RuntimeError(*[(arguments[i],) if result[i] is Tree.SEIZE else (arguments[i], result[i],) for i in range(len(arguments))])
    return result


class Tree:
    SEIZE = object()  # 占位符

    class Twig:
        def __init__(self, target, args=(), kwargs={}, log=lambda e: Log.e(loge(e))):
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
            for i in range(len(ret) - 1, -1, -1):
                if ret[i] is Tree.SEIZE:
                    ret.pop(i)
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
