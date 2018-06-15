#!/usr/local/bin/python3
# coding:utf-8
import threading
from decorator import synchronized


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


class _Base:
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

    # 串联
    @classmethod
    def series(cls, child, pipe=None):
        """
        pipe: object -> Arguments
        """
        pipe = pipe if pipe is not None else lambda o: Arguments(o)
        return _series(cls, child, pipe)

    # 并联
    @classmethod
    def parallel(cls, *wives, pipe=None):
        """
        pipe: *args, **kwargs -> Arguments[]
        """
        pipe = pipe if pipe is not None else lambda *args, **kwargs: [Arguments(*args, **kwargs) for i in range(len(wives) + 1)]

        class Pipes:
            def __init__(self, pipe):
                self.pipe = pipe

            def __call__(self, i, l):
                def pipe(*args, **kwargs):
                    if i == l - 1:
                        self.result = self.pipe(*args, **kwargs)
                    r = (self.result[i], self.result[i + 1],)
                    if i == 0:
                        del self.result
                    return r
                return pipe
        pipes = Pipes(pipe)
        cls = cls.output(lambda o: (o,))
        for i in range(len(wives)):
            cls = _parallel(cls, wives[i], pipes(i, len(wives)))
            cls = cls.output(lambda o: o[0] + (o[1],))
        return cls


def _series(Parent, Child, Pipe):
    class Series(_Base):
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
    class Parallel(_Base):
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


# 继承
def extends(Class):
    class Extends(Class, _Base):
        pass
    return Extends
