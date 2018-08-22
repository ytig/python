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
                for i in obj.__loop__:
                    if i['runnable'] is self:
                        generator = i['generator']
                        break
            if generator is not None:
                try:
                    delay = generator.send(obj)
                    assert isinstance(delay, numbers.Real)
                except BaseException as e:
                    with Lock(obj):
                        for i in range(len(obj.__loop__)):
                            if obj.__loop__[i]['runnable'] is self:
                                obj.__loop__.pop(i)
                                break
                    if not isinstance(e, StopIteration):
                        raise
                else:
                    with Lock(obj):
                        for i in obj.__loop__:
                            if i['runnable'] is self:
                                type(obj).__LOOP__.enter(delay, self)
                                break


class Looper(ABMeta):
    @staticmethod
    def __new__(*args, **kwargs):
        __LOOP__ = Loop()  # 循环器

        def __init__(self, *args, **kwargs):
            self.__loop__ = []
            self.__shutdown__ = False
            return invoke(None)

        # 开始（异常中断）
        def loop_enter(self, generator, important):
            with Lock(module()):
                assert inspect.getgeneratorstate(generator) == inspect.GEN_CREATED
                delay = generator.send(None)
                assert isinstance(delay, numbers.Real)
            with Lock(self):
                if important or not self.__shutdown__:
                    runnable = _weakrunnable(self)
                    eid = type(self).__LOOP__.enter(delay, runnable)
                    self.__loop__.append({
                        'eid': eid,
                        'runnable': runnable,
                        'generator': generator,
                        'important': important,
                    })
                    return eid

        # 延时
        def loop_delay(self, time, call, args=(), kwargs={}):
            def g():
                obj = yield time
                if isinstance(call, str):
                    getattr(obj, call)(*args, **kwargs)
                else:
                    call(*args, **kwargs)
                del obj
            return self.loop_enter(g(), True)

        # 循环
        def loop_circle(self, time, call, args=(), kwargs={}):
            def g():
                while True:
                    obj = yield time
                    if isinstance(call, str):
                        getattr(obj, call)(*args, **kwargs)
                    else:
                        call(*args, **kwargs)
                    del obj
            return self.loop_enter(g(), False)

        # 取消
        def loop_cancel(self, generics):
            ret = 0
            with Lock(self):
                for i in range(len(self.__loop__) - 1, -1, -1):
                    p = False
                    if generics is None:
                        p = True
                    elif inspect.isgenerator(generics):
                        p = self.__loop__[i]['generator'] is generics
                    elif isinstance(generics, int):
                        p = self.__loop__[i]['eid'] == generics
                    if p:
                        type(self).__LOOP__.cancel(self.__loop__[i]['runnable'])
                        self.__loop__.pop(i)
                        ret += 1
            return ret

        def __bef__(self):
            with Lock(self):
                self.__shutdown__ = True
                for i in range(len(self.__loop__) - 1, -1, -1):
                    if not self.__loop__[i]['important']:
                        type(self).__LOOP__.cancel(self.__loop__[i]['runnable'])
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
                    type(self).__LOOP__.cancel(i['runnable'])
                self.__loop__.clear()
            return ret
        return define(__class__)
