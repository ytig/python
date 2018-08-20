#!/usr/local/bin/python3
import inspect
import threading
import contextlib
import collections
from decorator import ilock
from task import Tree


# 上下文管理器（装饰器）
def withas(generics):
    if inspect.isclass(generics):
        if issubclass(generics, _baseclass):
            return generics
        else:
            class _class(_baseclass):
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs
                    self.__obj = Stack()

                def __enter__(self):
                    obj = generics(*self.args, **self.kwargs)
                    o = obj.__enter__()
                    self.__obj.push(obj)
                    return o

                def __exit__(self, t, v, tb):
                    obj = self.__obj.pop()
                    return obj.__exit__(t, v, tb)
            return _class
    elif inspect.isfunction(generics):
        if inspect.isgeneratorfunction(generics):
            generics = contextlib.contextmanager(generics)

            class _generatorfunction(_baseclass):
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs
                    self.__obj = Stack()

                def __enter__(self):
                    obj = generics(*self.args, **self.kwargs)
                    o = obj.__enter__()
                    self.__obj.push(obj)
                    return o

                def __exit__(self, t, v, tb):
                    obj = self.__obj.pop()
                    return obj.__exit__(t, v, tb)
            return _generatorfunction
        else:
            class _function(_baseclass):
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs

                def __enter__(self):
                    return generics(*self.args, **self.kwargs)

                def __exit__(self, t, v, tb):
                    pass
            return _function


# 执行器
def tree(t, log=None):
    if t <= 0:
        def _tree(cpu, *mems):
            ret = []
            for mem in mems:
                try:
                    ret.append(cpu(mem))
                except BaseException as e:
                    try:
                        log(e)
                    except BaseException:
                        pass
            return ret
        return _tree
    else:
        def _tree(cpu, *mems):
            return Tree(cpu, *mems, log=log).plant(t=t)
        return _tree


class _baseclass:
    # 输入转换
    @classmethod
    def input(this, pipe):
        """
        pipe: *args, **kwargs -> Arguments
        """
        series = _baseclass.__dict__['series'].__func__
        return series(lambda *args, **kwargs: (args, kwargs,), this, pipe=lambda t: pipe(*t[0], **t[1]))

    # 输出转换
    @classmethod
    def output(this, pipe):
        """
        pipe: object -> object
        """
        series = _baseclass.__dict__['series'].__func__
        return series(this, pipe)

    # 串联流程
    @classmethod
    def series(parent, child, pipe=lambda o: Arguments(o)):
        """
        pipe: object -> Arguments
        """
        parent = withas(parent)
        child = withas(child)

        def _series(*args, **kwargs):
            y = False
            pstack = (lambda i: [i, i.__enter__(), ])(parent(*args, **kwargs))
            try:
                cstack = (lambda i: [i, i.__enter__(), ])(pipe(pstack.pop())(child))
                try:
                    y = True
                    yield cstack.pop()
                except BaseException as e:
                    if cstack.pop().__exit__(type(e), e, e.__traceback__) is not True:
                        raise
                else:
                    cstack.pop().__exit__(None, None, None)
            except BaseException as e:
                if pstack.pop().__exit__(type(e), e, e.__traceback__) is not True:
                    raise
                if not y:
                    yield None
            else:
                pstack.pop().__exit__(None, None, None)
        return withas(_series)

    # 并联流程
    @classmethod
    def parallel(husband, *wives, pipe=lambda *args, **kwargs: [Arguments(*args, **kwargs), ], core=tree(0)):
        """
        pipe: *args, **kwargs -> Arguments[]
        """
        humans = [withas(i) for i in (husband,) + wives]

        def enter(args):
            call = args[0]
            arguments = args[1]
            obj = arguments(call)
            return [obj, obj.__enter__(), ]

        def exit(args):
            obj = args[0]
            e = args[1]
            if e is None:
                return obj.__exit__(None, None, None)
            else:
                return obj.__exit__(type(e), e, e.__traceback__)

        def _parallel(*args, **kwargs):
            p = [list(pipe(*args, **kwargs)), ]
            p[0] += [Arguments() for i in range(len(humans) - len(p[0]))]
            stacks = core(enter, *[t for t in zip(humans, p.pop())])
            try:
                assert len(stacks) == len(humans), 'parallel enter error'
            except BaseException:
                for s in stacks:
                    s.pop()
                assert len(core(exit, *[(s.pop(), None,) for s in stacks])) == len(stacks), 'parallel exit error'
                raise
            else:
                try:
                    yield [s.pop() for s in stacks]
                except BaseException as e:
                    assert len(core(exit, *[(s.pop(), e,) for s in stacks])) == len(stacks), 'parallel exit error'
                    raise
                else:
                    assert len(core(exit, *[(s.pop(), None,) for s in stacks])) == len(stacks), 'parallel exit error'
        return withas(_parallel)

    # 分支流程
    @classmethod
    def branch(parent, child, pipe=lambda o: Arguments(o), core=tree(0)):
        """
        pipe: object -> Arguments
        """
        parent = withas(parent)
        child = withas(child)

        def enter(args):
            call = args[0]
            arguments = args[1]
            obj = arguments(call)
            return [obj, obj.__enter__(), ]

        def exit(args):
            obj = args[0]
            e = args[1]
            if e is None:
                return obj.__exit__(None, None, None)
            else:
                return obj.__exit__(type(e), e, e.__traceback__)

        def _branch(*args, **kwargs):
            y = False
            pstack = (lambda i: [i, i.__enter__(), ])(parent(*args, **kwargs))
            try:
                try:
                    p = pstack.pop()
                    assert isinstance(p, collections.Iterable), 'branch init error'
                    p = list(p)
                    l = len(p)
                    pstack.append(p)
                    p = None
                except BaseException:
                    p = None
                    raise
                else:
                    cstacks = core(enter, *[(child, pipe(o),) for o in pstack.pop()])
                    try:
                        assert len(cstacks) == l, 'branch enter error'
                    except BaseException:
                        for s in cstacks:
                            s.pop()
                        assert len(core(exit, *[(s.pop(), None,) for s in cstacks])) == len(cstacks), 'branch exit error'
                        raise
                    else:
                        try:
                            y = True
                            yield [s.pop() for s in cstacks]
                        except BaseException as e:
                            assert len(core(exit, *[(s.pop(), e,) for s in cstacks])) == len(cstacks), 'branch exit error'
                            raise
                        else:
                            assert len(core(exit, *[(s.pop(), None,) for s in cstacks])) == len(cstacks), 'branch exit error'
            except BaseException as e:
                if pstack.pop().__exit__(type(e), e, e.__traceback__) is not True:
                    raise
                if not y:
                    yield []
            else:
                pstack.pop().__exit__(None, None, None)
        return withas(_branch)

    # 合并流程
    @classmethod
    def merge(husband, wife, pipe):
        """
        pipe: *args, **kwargs -> bool
        """
        husband = withas(husband)
        wife = withas(wife)

        def _merge(*args, **kwargs):
            stack = (lambda i: [i, i.__enter__(), ])((husband if not pipe(*args, **kwargs) else wife)(*args, **kwargs))
            try:
                yield stack.pop()
            except BaseException as e:
                if stack.pop().__exit__(type(e), e, e.__traceback__) is not True:
                    raise
            else:
                stack.pop().__exit__(None, None, None)
        return withas(_merge)


class Stack:
    def __init__(self):
        self.values = {}

    # 入栈
    @ilock()
    def push(self, data):
        key = threading.currentThread().name
        if key not in self.values:
            self.values[key] = []
        self.values[key].append(data)

    # 出栈
    @ilock()
    def pop(self):
        key = threading.currentThread().name
        return self.values[key].pop()


class Arguments:
    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = dict(kwargs)

    # 追加不定长参数
    def extend(self, *args):
        self.args.extend(args)

    # 更新关键字参数
    def update(self, **kwargs):
        self.kwargs.update(kwargs)

    # 调用函数
    def __call__(self, call):
        return call(*self.args, **self.kwargs)
