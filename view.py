#!/usr/local/bin/python3
import weakref
from decorator import classOf, Lock
from loop import Loop
from ab import attribute, ABMeta


class runnable:
    def __init__(self, *args, **kwargs):
        if len(args) <= 0:
            raise Exception('no func.')
        func = args[0]
        args = args[1:]
        self.func = func
        self.args = args
        self.kwargs = kwargs

    # 执行
    def __call__(self):
        return self.func(*self.args, **self.kwargs)

    # 延时
    def delay(self, time, v=None):
        def generator():
            yield time
            self()
        g = generator()
        if v is not None:
            v.do(g, important=True)
        return g

    # 循环
    def circle(self, time, v=None):
        def generator():
            while True:
                yield time
                self()
        g = generator()
        if v is not None:
            v.do(g, important=False)
        return g


def _weakrunnable(self):
    ref = weakref.ref(self)

    def runnable():
        self = ref()
        if self is not None:
            generator = None
            with Lock(self):
                for g, r, i, in self.__loop__:
                    if r is runnable:
                        generator = g
                        break
            if generator is not None:
                try:
                    delay = next(generator)
                except BaseException:
                    with Lock(self):
                        for i in range(len(self.__loop__)):
                            if self.__loop__[i][1] is runnable:
                                self.__loop__.pop(i)
                                break
                else:
                    with Lock(self):
                        for g, r, i, in self.__loop__:
                            if r is runnable:
                                self.__class__.DO(runnable, delay)
                                break
    return runnable


class View(ABMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        attr = attribute(bases, namespace)

        def __init__(self, *args, **kwargs):
            self.__loop__ = []
            self.__shutdown__ = False
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
        attr.setattr('__init__', __init__)

        # 执行
        def do(self, generator, important):
            try:
                delay = next(generator)
            except BaseException:
                pass
            else:
                with Lock(self):
                    if important or not self.__shutdown__:
                        runnable = _weakrunnable(self)
                        self.__loop__.append((generator, runnable, important,))
                        self.__class__.DO(runnable, delay)
        namespace['do'] = do

        # 取消执行
        def undo(self, generator):
            r = 0
            with Lock(self):
                for i in range(len(self.__loop__) - 1, -1, -1):
                    if self.__loop__[i][0] is generator:
                        self.__class__.UNDO(self.__loop__[i][1])
                        self.__loop__.pop(i)
                        r += 1
            return r
        namespace['undo'] = undo

        def __bef__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
            with Lock(self):
                self.__shutdown__ = True
                for i in range(len(self.__loop__) - 1, -1, -1):
                    if not self.__loop__[i][2]:
                        self.__class__.UNDO(self.__loop__[i][1])
                        self.__loop__.pop(i)
        attr.setattr('__bef__', __bef__)

        def __aft__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
            self.__del__()
        attr.setattr('__aft__', __aft__)

        def __del__(self, *args, **kwargs):
            func = args[0]
            args = args[1:]
            if callable(func):
                func(self, *args, **kwargs)
            for i in self.__loop__:
                self.__class__.UNDO(i[1])
            self.__loop__.clear()
        attr.setattr('__del__', __del__)
        return super().__new__(mcls, name, bases, namespace, **kwargs)

    # 执行
    def DO(cls, *args, **kwargs):
        with Lock(classOf(cls)):
            if not hasattr(cls, '__LOOP__'):
                cls.__LOOP__ = Loop()
        return cls.__LOOP__.do(*args, **kwargs)

    # 取消执行
    def UNDO(cls, *args, **kwargs):
        with Lock(classOf(cls)):
            if not hasattr(cls, '__LOOP__'):
                cls.__LOOP__ = Loop()
        return cls.__LOOP__.undo(*args, **kwargs)
