#!/usr/local/bin/python3
import numbers
import inspect
import weakref
from decorator import moduleOf, classOf, Lock
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


class _weakrunnable:
    def __init__(self, obj):
        self.ref = weakref.ref(obj)

    def __call__(self):
        obj = self.ref()
        if obj is not None:
            generator = None
            with Lock(obj):
                for w, g, i, p, in obj.__loop__:
                    if w is self:
                        generator = g
                        break
            if generator is not None:
                try:
                    delay = generator.send(obj)
                    assert isinstance(delay, numbers.Real)
                except BaseException:
                    with Lock(obj):
                        for i in range(len(obj.__loop__)):
                            if obj.__loop__[i][0] is self:
                                obj.__loop__.pop(i)
                                break
                else:
                    with Lock(obj):
                        for w, g, i, p, in obj.__loop__:
                            if w is self:
                                obj.__class__.DO(self, delay)
                                break


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

        # 执行（异常中断）
        def do(self, generator, important):
            try:
                with Lock(moduleOf(__class__)):
                    assert inspect.getgeneratorstate(generator) == inspect.GEN_CREATED
                    delay = generator.send(None)
                    assert isinstance(delay, numbers.Real)
            except BaseException:
                pass
            else:
                with Lock(self):
                    if important or not self.__shutdown__:
                        weakrunnable = _weakrunnable(self)
                        pid = self.__class__.DO(weakrunnable, delay)
                        self.__loop__.append((weakrunnable, generator, important, pid,))
                        return pid
        namespace['do'] = do

        # 取消执行
        def undo(self, generics):
            r = 0
            with Lock(self):
                for i in range(len(self.__loop__) - 1, -1, -1):
                    p = False
                    if generics is None:
                        p = True
                    elif inspect.isgenerator(generics):
                        p = self.__loop__[i][1] is generics
                    elif isinstance(generics, int):
                        p = self.__loop__[i][3] == generics
                    if p:
                        self.__class__.UNDO(self.__loop__[i][0])
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
                        self.__class__.UNDO(self.__loop__[i][0])
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
            with Lock(self):
                for i in self.__loop__:
                    self.__class__.UNDO(i[0])
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
