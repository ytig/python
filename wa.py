#!/usr/local/bin/python3
import inspect
import contextlib
import collections
from kit import getvar, setvar
from decorator import Lock
from task import Tree


# 上下文管理器（装饰器）
def withas(generics):
    if inspect.isclass(generics):
        if issubclass(generics, _baseclass):
            return generics
        else:
            class _class(_baseclass):
                def _init(self, *args, **kwargs):
                    self.stack = [Arguments(*args, **kwargs), ]

                def _enter(self):
                    obj = self.stack.pop()(generics)
                    ret = obj.__enter__()
                    self.stack.append(obj)
                    return ret

                def _exit(self, t, v, tb):
                    return self.stack.pop().__exit__(t, v, tb)
            return _class
    elif inspect.isfunction(generics):
        if inspect.isgeneratorfunction(generics):
            generics = contextlib.contextmanager(generics)

            class _generatorfunction(_baseclass):
                def _init(self, *args, **kwargs):
                    self.stack = [Arguments(*args, **kwargs), ]

                def _enter(self):
                    obj = self.stack.pop()(generics)
                    ret = obj.__enter__()
                    self.stack.append(obj)
                    return ret

                def _exit(self, t, v, tb):
                    return self.stack.pop().__exit__(t, v, tb)
            return _generatorfunction
        else:
            class _function(_baseclass):
                def _init(self, *args, **kwargs):
                    self.stack = [Arguments(*args, **kwargs), ]

                def _enter(self):
                    return self.stack.pop()(generics)
            return _function
    else:
        class _object(_baseclass):
            def _enter(self):
                return generics
        return _object


# 执行器
def tree(t, log=None):
    T = Tree(0 if t < 0 else t)
    return lambda target, *tuples: T.plant(*[Tree.Twig(target, args=args, log=log) for args in tuples])


def _strict(i):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            with Lock(self):
                assert getvar(self, '__withas__', d=0) == i and setvar(self, '__withas__', i + 1)
            try:
                return function(self, *args, **kwargs)
            except BaseException:
                with Lock(self):
                    assert setvar(self, '__withas__', -1)
                raise
        return wrapper
    return decorator


def _enter(cls, arguments):
    self = arguments(cls)
    return [self, self.__enter__(), ]


def _exit(self, e):
    if e is None:
        return self.__exit__(None, None, None)
    else:
        return self.__exit__(type(e), e, e.__traceback__)


class _baseclass:
    @_strict(0)
    def __init__(self, *args, **kwargs):
        return self._init(*args, **kwargs)

    @_strict(1)
    def __enter__(self):
        return self._enter()

    @_strict(2)
    def __exit__(self, t, v, tb):
        return self._exit(t, v, tb)

    def _init(self):
        pass

    def _enter(self):
        pass

    def _exit(self, t, v, tb):
        pass

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
            pstack = _enter(parent, Arguments(*args, **kwargs))
            try:
                cstack = _enter(child, Arguments.make(pipe(pstack.pop())))
                try:
                    y = True
                    yield cstack.pop()
                except BaseException as e:
                    if _exit(cstack.pop(), e) is not True:
                        raise
                else:
                    _exit(cstack.pop(), None)
            except BaseException as e:
                if _exit(pstack.pop(), e) is not True:
                    raise
                if not y:
                    yield None
            else:
                _exit(pstack.pop(), None)
        return withas(_series)

    # 并联流程
    @classmethod
    def parallel(husband, *wives, pipe=lambda *args, **kwargs: [Arguments(*args, **kwargs), ], core=tree(0)):
        """
        pipe: *args, **kwargs -> Arguments[]
        core: target, *tuples -> object[]
        """
        humans = [withas(i) for i in (husband,) + wives]

        def _pipe(*args, **kwargs):
            r = pipe(*args, **kwargs)
            return [Arguments.make(g) for g in r] + [Arguments()] * (len(humans) - len(r))

        def _parallel(*args, **kwargs):
            stacks = core(_enter, *[t for t in zip(humans, _pipe(*args, **kwargs))])
            try:
                assert len(stacks) == len(humans), 'parallel enter error'
            except BaseException:
                for s in stacks:
                    s.pop()
                assert len(core(_exit, *[(s.pop(), None,) for s in stacks])) == len(stacks), 'parallel exit error'
                raise
            else:
                try:
                    yield [s.pop() for s in stacks]
                except BaseException as e:
                    assert len(core(_exit, *[(s.pop(), e,) for s in stacks])) == len(stacks), 'parallel exit error'
                    raise
                else:
                    assert len(core(_exit, *[(s.pop(), None,) for s in stacks])) == len(stacks), 'parallel exit error'
        return withas(_parallel)

    # 分支流程
    @classmethod
    def branch(parent, child, pipe=lambda o: Arguments(o), core=tree(0)):
        """
        pipe: object -> Arguments
        core: target, *tuples -> object[]
        """
        parent = withas(parent)
        child = withas(child)

        def _branch(*args, **kwargs):
            y = False
            pstack = _enter(parent, Arguments(*args, **kwargs))
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
                    cstacks = core(_enter, *[(child, Arguments.make(pipe(o)),) for o in pstack.pop()])
                    try:
                        assert len(cstacks) == l, 'branch enter error'
                    except BaseException:
                        for s in cstacks:
                            s.pop()
                        assert len(core(_exit, *[(s.pop(), None,) for s in cstacks])) == len(cstacks), 'branch exit error'
                        raise
                    else:
                        try:
                            y = True
                            yield [s.pop() for s in cstacks]
                        except BaseException as e:
                            assert len(core(_exit, *[(s.pop(), e,) for s in cstacks])) == len(cstacks), 'branch exit error'
                            raise
                        else:
                            assert len(core(_exit, *[(s.pop(), None,) for s in cstacks])) == len(cstacks), 'branch exit error'
            except BaseException as e:
                if _exit(pstack.pop(), e) is not True:
                    raise
                if not y:
                    yield []
            else:
                _exit(pstack.pop(), None)
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
            stack = _enter(husband if not pipe(*args, **kwargs) else wife, Arguments(*args, **kwargs))
            try:
                yield stack.pop()
            except BaseException as e:
                if _exit(stack.pop(), e) is not True:
                    raise
            else:
                _exit(stack.pop(), None)
        return withas(_merge)


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

    # 构造参数
    @staticmethod
    def make(generics):
        if isinstance(generics, Arguments):
            return generics
        elif isinstance(generics, tuple):
            return Arguments(*generics)
        elif isinstance(generics, dict):
            return Arguments(**generics)
        elif isinstance(generics, collections.Iterable):
            arguments = list(generics)
            if len(arguments) == 2 and isinstance(arguments[0], tuple) and isinstance(arguments[1], dict):
                return Arguments(*arguments[0], **arguments[1])
        raise TypeError
