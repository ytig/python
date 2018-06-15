#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import synchronized
from log import Log
TAG = 'wa'


class Stack:
    def __init__(self):
        self.values = {}

    # 入栈
    @synchronized()
    def push(self, data):
        key = threading.currentThread().name
        value = self.values.get(key)
        if value is None:
            value = []
            self.values[key] = value
        value.append(data)

    # 出栈
    @synchronized()
    def pop(self):
        key = threading.currentThread().name
        value = self.values.get(key)
        return value.pop()


class Arguments:
    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = dict(kwargs)

    # 追加不定长参数（必备参数）
    def extend(self, *args):
        self.args.extend(args)
        return self

    # 更新关键字参数（默认参数）
    def update(self, **kwargs):
        self.kwargs.update(kwargs)
        return self

    # 调用函数
    def __call__(self, callable):
        return callable(*self.args, **self.kwargs)


class _Class:
    # 输入转换
    @classmethod
    def input(cls, pipe=None):
        """
        pipe: *args, **kwargs -> Arguments
        """
        pipe = pipe if pipe is not None else lambda *args, **kwargs: Arguments(*args, **kwargs)

        class parent:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def __enter__(self):
                return self

            def __exit__(self, type, value, traceback):
                pass
        return _series(parent, cls, lambda self: pipe(*self.args, **self.kwargs))

    # 输出转换
    @classmethod
    def output(cls, pipe=None):
        """
        pipe: object -> object
        """
        pipe = pipe if pipe is not None else lambda o: o

        class child:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def __enter__(self):
                return pipe(self.args[0])

            def __exit__(self, type, value, traceback):
                pass
        return _series(cls, child, lambda o: Arguments(o))

    # 串联流程
    @classmethod
    def series(cls, child, pipe=None):
        """
        pipe: object -> Arguments
        """
        pipe = pipe if pipe is not None else lambda o: Arguments(o)
        return _series(cls, child, pipe)

    # 并联流程
    @classmethod
    def parallel(cls, *wives, pipe=None):
        """
        pipe: *args, **kwargs -> Arguments[]
        """
        l = len(wives)
        pipe = pipe if pipe is not None else lambda *args, **kwargs: [Arguments(*args, **kwargs) for i in range(l + 1)]

        def pipes(i):
            def p(*args, **kwargs):
                if i == l - 1:
                    result = pipe(*args, **kwargs)
                else:
                    result = args[0]
                if i == 0:
                    return (result[i], result[i + 1],)
                else:
                    return (Arguments(result), result[i + 1],)
            return p
        cls = cls.output(lambda o: (o,))
        for i in range(l):
            cls = _parallel(cls, wives[i], pipes(i))
            cls = cls.output(lambda o: o[0] + (o[1],))
        return cls

    # 分叉流程
    @classmethod
    def branch(cls, child, pipe=None, log=lambda e: Log.e(e, tag=TAG)):
        """
        pipe: object -> Arguments
        """
        pipe = pipe if pipe is not None else lambda o: Arguments(o)
        return _branch(cls, child, pipe, log)


def _series(Parent, Child, Pipe):
    class Series(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__parent = Stack()
            self.__child = Stack()

        def __enter__(self):
            parent = Parent(*self.args, **self.kwargs)
            p = parent.__enter__()
            try:
                child = Pipe(p)(Child)
                c = child.__enter__()
                self.__parent.push(parent)
                self.__child.push(child)
                return c
            except BaseException as e:
                parent.__exit__(e.__class__, e, e.__traceback__)
                raise e

        def __exit__(self, type, value, traceback):
            child = self.__child.pop()
            parent = self.__parent.pop()
            try:
                child.__exit__(type, value, traceback)
            except BaseException as e:
                parent.__exit__(e.__class__, e, e.__traceback__)
                raise e
            parent.__exit__(type, value, traceback)
    return Series


def _parallel(Husband, Wife, Pipe):
    class Parallel(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__husband = Stack()
            self.__wife = Stack()

        def __enter__(self):
            arguments = Pipe(*self.args, **self.kwargs)
            husband = arguments[0](Husband)
            h = husband.__enter__()
            try:
                wife = arguments[1](Wife)
                w = wife.__enter__()
                self.__husband.push(husband)
                self.__wife.push(wife)
                return (h, w,)
            except BaseException as e:
                husband.__exit__(e.__class__, e, e.__traceback__)
                raise e

        def __exit__(self, type, value, traceback):
            wife = self.__wife.pop()
            husband = self.__husband.pop()
            try:
                wife.__exit__(type, value, traceback)
            except BaseException as e:
                husband.__exit__(e.__class__, e, e.__traceback__)
                raise e
            husband.__exit__(type, value, traceback)
    return Parallel


def _branch(Parent, Child, Pipe, Log):
    def log(e):
        try:
            Log(e)
        except BaseException:
            pass

    class Branch(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__parent = Stack()
            self.__children = Stack()

        def __enter__(self):
            parent = Parent(*self.args, **self.kwargs)
            ps = parent.__enter__()
            children = []
            cs = []
            try:
                for p in ps:
                    try:
                        child = Pipe(p)(Child)
                        c = child.__enter__()
                        cs.append(c)
                        children.append(child)
                    except BaseException as e:
                        log(e)
            except BaseException as e:
                log(e)
            self.__parent.push(parent)
            self.__children.push(children)
            return tuple(cs)

        def __exit__(self, type, value, traceback):
            children = self.__children.pop()
            parent = self.__parent.pop()
            try:
                for child in children:
                    try:
                        child.__exit__(type, value, traceback)
                    except BaseException as e:
                        log(e)
            except BaseException as e:
                log(e)
            parent.__exit__(type, value, traceback)
    return Branch


# 追加（装饰器）
def extends(Class):
    class Extends(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__object = Stack()

        def __enter__(self):
            object = Class(*self.args, **self.kwargs)
            o = object.__enter__()
            self.__object.push(object)
            return o

        def __exit__(self, type, value, traceback):
            object = self.__object.pop()
            object.__exit__(type, value, traceback)
    return Extends


# 更新（装饰器）
def updates(Def):
    class Updates(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return Def(*self.args, **self.kwargs)

        def __exit__(self, type, value, traceback):
            pass
    return Updates
