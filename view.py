#!/usr/local/bin/python3
import numbers
import inspect
import weakref
from kit import hasvar, getvar, setvar, module
from decorator import Lock
from loop import Loop
from ab import attribute, ABMeta


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
                with Lock(module()):
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
        assert not attr.hasattr('do')
        namespace['do'] = do

        # 延时执行
        def doDelay(self, time, func, args=(), kwargs={}):
            def g():
                obj = yield time
                func(obj, *args, **kwargs)
                del obj
            return self.do(g(), True)
        assert not attr.hasattr('doDelay')
        namespace['doDelay'] = doDelay

        # 循环执行
        def doCircle(self, time, func, args=(), kwargs={}):
            def g():
                while True:
                    obj = yield time
                    func(obj, *args, **kwargs)
                    del obj
            return self.do(g(), False)
        assert not attr.hasattr('doCircle')
        namespace['doCircle'] = doCircle

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
                        self.__class__.UNDO(self.__loop__[i][0])
                        self.__loop__.pop(i)
                        ret += 1
            return ret
        assert not attr.hasattr('undo')
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
        name = '__LOOP__'
        with Lock(cls):
            assert hasvar(cls, name) or setvar(cls, name, Loop())
        return getvar(cls, name).do(*args, **kwargs)

    # 取消执行
    def UNDO(cls, *args, **kwargs):
        name = '__LOOP__'
        with Lock(cls):
            assert hasvar(cls, name) or setvar(cls, name, Loop())
        return getvar(cls, name).undo(*args, **kwargs)
