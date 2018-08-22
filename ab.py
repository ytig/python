#!/usr/local/bin/python3
import weakref
from kit import getvar, setvar, apply
from decorator import ilock, ithrow
from meta import define, invoke
from shutdown import bregister, aregister, unregister


class weakmethod:
    GC = object()  # 已回收

    def __init__(self, obj, name):
        self.ref = weakref.ref(obj)
        self.name = name

    def __call__(self, *args, **kwargs):
        obj = self.ref()
        if obj is not None:
            return apply(obj, self.name, *args, **kwargs)
        else:
            return weakmethod.GC


class ABMeta(type):
    @staticmethod
    def __new__(*args, **kwargs):
        def __init__(self, *args, **kwargs):
            setvar(self, '__weakbef__', weakmethod(self, '__bef__'))
            setvar(self, '__weakaft__', weakmethod(self, '__aft__'))
            ret = invoke(None)
            bregister(getvar(self, '__weakbef__'))
            aregister(getvar(self, '__weakaft__'))
            return ret

        def __bef__(self):
            return invoke(None)

        def __aft__(self):
            return invoke(None)

        @ilock()
        @ithrow()
        def __del__(self):
            unregister(getvar(self, '__weakaft__'))
            unregister(getvar(self, '__weakbef__'))
            return invoke(None)
        return define(__class__)
