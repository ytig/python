#!/usr/local/bin/python3
import numbers
import inspect
import weakref
from kit import module
from decorator import Lock
from meta import define, invoke
from ab import ABMeta
from loop import Loop


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
                except BaseException as e:
                    with Lock(obj):
                        for i in range(len(obj.__loop__)):
                            if obj.__loop__[i][0] is self:
                                obj.__loop__.pop(i)
                                break
                    if not isinstance(e, StopIteration):
                        raise
                else:
                    with Lock(obj):
                        for w, g, i, p, in obj.__loop__:
                            if w is self:
                                type(obj).__LOOP__.do(self, delay)
                                break


class Looper(ABMeta):
    @staticmethod
    def __new__(*args, **kwargs):
        __LOOP__ = Loop()  # 循环器

        def __init__(self, *args, **kwargs):
            self.__loop__ = []
            self.__shutdown__ = False
            return invoke(None)

        # 执行（异常中断）
        def do(self, generator, important):
            with Lock(module()):
                assert inspect.getgeneratorstate(generator) == inspect.GEN_CREATED
                delay = generator.send(None)
                assert isinstance(delay, numbers.Real)
            with Lock(self):
                if important or not self.__shutdown__:
                    weakrunnable = _weakrunnable(self)
                    pid = type(self).__LOOP__.do(weakrunnable, delay)
                    self.__loop__.append((weakrunnable, generator, important, pid,))
                    return pid

        # 延时执行
        def doDelay(self, func, time, args=(), kwargs={}):
            def g():
                obj = yield time
                func(obj, *args, **kwargs)
                del obj
            return self.do(g(), True)

        # 循环执行
        def doCircle(self, func, time, args=(), kwargs={}):
            def g():
                while True:
                    obj = yield time
                    func(obj, *args, **kwargs)
                    del obj
            return self.do(g(), False)

        # 取消执行
        def undo(self, generics):
            ret = 0
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
                        type(self).__LOOP__.undo(self.__loop__[i][0])
                        self.__loop__.pop(i)
                        ret += 1
            return ret

        def __bef__(self):
            with Lock(self):
                self.__shutdown__ = True
                for i in range(len(self.__loop__) - 1, -1, -1):
                    if not self.__loop__[i][2]:
                        type(self).__LOOP__.undo(self.__loop__[i][0])
                        self.__loop__.pop(i)
            return invoke(None)

        def __aft__(self):
            ret = invoke(None)
            self.__del__()
            return ret

        def __del__(self):
            ret = invoke(None)
            with Lock(self):
                for i in self.__loop__:
                    type(self).__LOOP__.undo(i[0])
                self.__loop__.clear()
            return ret
        return define(__class__)
