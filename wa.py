#!/usr/local/bin/python3
import threading
from decorator import ilock


class Stack:
    def __init__(self):
        self.values = {}

    # 入栈
    @ilock()
    def push(self, data):
        key = threading.currentThread().name
        value = self.values.get(key)
        if value is None:
            value = []
            self.values[key] = value
        value.append(data)

    # 出栈
    @ilock()
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

        class Parent:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def __enter__(self):
                return self

            def __exit__(self, t, v, tb):
                pass
        return _series(Parent, cls, lambda self: pipe(*self.args, **self.kwargs))

    # 输出转换
    @classmethod
    def output(cls, pipe=None):
        """
        pipe: object -> object
        """
        pipe = pipe if pipe is not None else lambda o: o

        class Child:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def __enter__(self):
                return pipe(self.args[0])

            def __exit__(self, t, v, tb):
                pass
        return _series(cls, Child, lambda o: Arguments(o))

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

    # 分支流程
    @classmethod
    def branch(cls, child, pipe=None):
        """
        pipe: object -> Arguments
        """
        pipe = pipe if pipe is not None else lambda o: Arguments(o)
        return _branch(cls, child, pipe)

    # 合并流程
    @classmethod
    def merge(cls, wife, pipe=None):
        """
        pipe: *args, **kwargs -> bool
        """
        pipe = pipe if pipe is not None else lambda *args, **kwargs: False
        return _merge(cls, wife, pipe)


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
                parent.__exit__(type(e), e, e.__traceback__)
                raise

        def __exit__(self, t, v, tb):
            child = self.__child.pop()
            parent = self.__parent.pop()
            try:
                child.__exit__(t, v, tb)
            except BaseException as e:
                parent.__exit__(type(e), e, e.__traceback__)
                raise
            parent.__exit__(t, v, tb)
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
                husband.__exit__(type(e), e, e.__traceback__)
                raise

        def __exit__(self, t, v, tb):
            wife = self.__wife.pop()
            husband = self.__husband.pop()
            try:
                wife.__exit__(t, v, tb)
            except BaseException as e:
                husband.__exit__(type(e), e, e.__traceback__)
                raise
            husband.__exit__(t, v, tb)
    return Parallel


def _branch(Parent, Child, Pipe):
    def exits(queue, t, v, tb):
        if queue:
            exit = queue.pop()
            try:
                exit.__exit__(t, v, tb)
            except BaseException as e:
                exits(queue, type(e), e, e.__traceback__)
                raise
            exits(queue, t, v, tb)

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
                    child = Pipe(p)(Child)
                    cs.append(child.__enter__())
                    children.append(child)
            except BaseException as e:
                exits([parent] + children, type(e), e, e.__traceback__)
                raise
            self.__parent.push(parent)
            self.__children.push(children)
            return tuple(cs)

        def __exit__(self, t, v, tb):
            children = self.__children.pop()
            parent = self.__parent.pop()
            exits([parent] + children, t, v, tb)
    return Branch


def _merge(Husband, Wife, Pipe):
    class Merge(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__obj = Stack()

        def __enter__(self):
            obj = (Wife if Pipe(*self.args, **self.kwargs) else Husband)(*self.args, **self.kwargs)
            o = obj.__enter__()
            self.__obj.push(obj)
            return o

        def __exit__(self, t, v, tb):
            obj = self.__obj.pop()
            obj.__exit__(t, v, tb)
    return Merge


# 追加（装饰器）
def extends(Class):
    class Extends(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__obj = Stack()

        def __enter__(self):
            obj = Class(*self.args, **self.kwargs)
            o = obj.__enter__()
            self.__obj.push(obj)
            return o

        def __exit__(self, t, v, tb):
            obj = self.__obj.pop()
            obj.__exit__(t, v, tb)
    return Extends


# 更新（装饰器）
def updates(Def):
    class Updates(_Class):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return Def(*self.args, **self.kwargs)

        def __exit__(self, t, v, tb):
            pass
    return Updates
