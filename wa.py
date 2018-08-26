#!/usr/local/bin/python3
import inspect
import linecache
import contextlib
import collections
from kit import getvar, setvar, frames
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
                    del obj.func, obj.args, obj.kwds,
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
def tree(t):
    T = Tree(t)
    return lambda *tuples: T.plant(*[Tree.Twig(t[0], args=t[1:]) for t in tuples])


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
    return self.__exit__(*((None, None, None,) if e is None else (type(e), e, e.__traceback__,)))


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

    def __call__(self):
        with self as ret:
            return ret

    def _init(self):
        pass

    def _enter(self):
        pass

    def _exit(self, t, v, tb):
        pass

    # 串联流程
    @classmethod
    def series(parent, child, pipe=lambda *args, **kwargs: Arguments(args[0])):
        """
        pipe: return, *args, **kwargs -> Arguments
        """
        parent = withas(parent)
        child = withas(child)

        def _pipe(*args, **kwargs):
            return Arguments.make(pipe(*args, **kwargs))

        def _series(*args, **kwargs):
            y = False
            try:
                pstack = _enter(parent, Arguments(*args, **kwargs))
                pstack.append(Arguments(pstack.pop(), *args, **kwargs))
            finally:
                del args, kwargs,
            try:
                cstack = _enter(child, pstack.pop()(_pipe))
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
        core: *tuples -> return[]
        """
        humans = [withas(g) for g in (husband,) + wives]

        def _pipe(*args, **kwargs):
            return [Arguments.make(g) for g in pipe(*args, **kwargs)]

        def _call(*args):
            try:
                return (True, args[0](*args[1:]),)
            except BaseException as e:
                return (False, e,)

        def _core(*tuples):
            out = []
            err = []
            for t in core(*[(_call,) + t for t in tuples]):
                (out if t[0] else err).append(t[1])
            return (out, err,)

        def _parallel(*args, **kwargs):
            try:
                stacks, traces, = _core(*zip([_enter, ] * len(humans), humans, _pipe(*args, **kwargs) + [Arguments(), ] * len(humans)))
            finally:
                del args, kwargs,
            try:
                if traces:
                    traces = [traces, ]
                    raise EnterException(*traces.pop())
            except BaseException:
                for s in stacks:
                    s.pop()
                traces = _core(*[(_exit, s.pop(), None,) for s in stacks])[1]
                if traces:
                    traces = [traces, ]
                    raise ExitException(*traces.pop())
                raise
            else:
                try:
                    yield [s.pop() for s in stacks]
                except BaseException as e:
                    traces = _core(*[(_exit, s.pop(), e,) for s in stacks])[1]
                    if traces:
                        traces = [traces, ]
                        raise ExitException(*traces.pop())
                    raise
                else:
                    traces = _core(*[(_exit, s.pop(), None,) for s in stacks])[1]
                    if traces:
                        traces = [traces, ]
                        raise ExitException(*traces.pop())
        return withas(_parallel)

    # 分支流程
    @classmethod
    def branch(parent, child, pipe=lambda *args, **kwargs: Arguments(args[0]), core=tree(0)):
        """
        pipe: return, *args, **kwargs -> Arguments
        core: *tuples -> return[]
        """
        parent = withas(parent)
        child = withas(child)

        def _pipe(*args, **kwargs):
            ret = args[0]
            args = args[1:]
            return [Arguments.make(pipe(r, *args, **kwargs)) for r in ret]

        def _call(*args):
            try:
                return (True, args[0](*args[1:]),)
            except BaseException as e:
                return (False, e,)

        def _core(*tuples):
            out = []
            err = []
            for t in core(*[(_call,) + t for t in tuples]):
                (out if t[0] else err).append(t[1])
            return (out, err,)

        def _branch(*args, **kwargs):
            y = False
            try:
                pstack = _enter(parent, Arguments(*args, **kwargs))
                pstack.append(Arguments(pstack.pop(), *args, **kwargs))
            finally:
                del args, kwargs,
            try:
                cstacks, traces, = _core(*[(_enter, child, a,) for a in pstack.pop()(_pipe)])
                try:
                    if traces:
                        traces = [traces, ]
                        raise EnterException(*traces.pop())
                except BaseException:
                    for s in cstacks:
                        s.pop()
                    traces = _core(*[(_exit, s.pop(), None,) for s in cstacks])[1]
                    if traces:
                        traces = [traces, ]
                        raise ExitException(*traces.pop())
                    raise
                else:
                    try:
                        y = True
                        yield [s.pop() for s in cstacks]
                    except BaseException as e:
                        traces = _core(*[(_exit, s.pop(), e,) for s in cstacks])[1]
                        if traces:
                            traces = [traces, ]
                            raise ExitException(*traces.pop())
                        raise
                    else:
                        traces = _core(*[(_exit, s.pop(), None,) for s in cstacks])[1]
                        if traces:
                            traces = [traces, ]
                            raise ExitException(*traces.pop())
            except BaseException as e:
                if _exit(pstack.pop(), e) is not True:
                    raise
                if not y:
                    yield []
            else:
                _exit(pstack.pop(), None)
        return withas(_branch)

    # 条件流程
    @classmethod
    def either(husband, wife, pipe):
        """
        pipe: *args, **kwargs -> bool
        """
        husband = withas(husband)
        wife = withas(wife)

        def _either(*args, **kwargs):
            try:
                stack = _enter(husband if not pipe(*args, **kwargs) else wife, Arguments(*args, **kwargs))
            finally:
                del args, kwargs,
            try:
                yield stack.pop()
            except BaseException as e:
                if _exit(stack.pop(), e) is not True:
                    raise
            else:
                _exit(stack.pop(), None)
        return withas(_either)

    # 循环流程
    @classmethod
    def ditto(this, pipe):
        """
        pipe: return, *args, **kwargs -> Arguments or None
        """
        this = withas(this)

        def _pipe(*args, **kwargs):
            g = pipe(*args, **kwargs)
            if g is None:
                return (args, kwargs,)
            else:
                return Arguments.make(g)

        def __ditto(*args, **kwargs):
            y = args[-1]
            args = args[:-1]
            try:
                stack = _enter(this, Arguments(*args, **kwargs))
                stack.append(Arguments(stack.pop(), *args, **kwargs))
            finally:
                del args, kwargs,
            try:
                stack.append(stack.pop()(_pipe))
                if isinstance(stack[-1], Arguments):
                    yield from stack.pop().extend(y)(__ditto)
                else:
                    y[0] = True
                    yield stack.pop()[0][0]
            except BaseException as e:
                if _exit(stack.pop(), e) is not True:
                    raise
            else:
                _exit(stack.pop(), None)

        def _ditto(*args, **kwargs):
            y = [False, ]
            a = [Arguments(*args, y, **kwargs), ]
            del args, kwargs,
            yield from a.pop()(__ditto)
            if not y[0]:
                yield None
        return withas(_ditto)


class MultiException(Exception):
    @staticmethod
    def join(*exceptions):
        start = 'The exceptions are displayed below.\n\n'
        end = '\n\n...Display completed.'
        strings = []
        for v in exceptions:
            t = type(v)
            assert issubclass(t, BaseException)
            try:
                string = ''
                if issubclass(t, MultiException):
                    s = str(v)
                    string += s[len(start):len(s) - len(end)]
                elif issubclass(t, SyntaxError):
                    string += '  File "{}", line {}\n'.format(v.filename, v.lineno)
                    string += '    {}\n'.format(v.text.strip())
                    if v.offset is not None:
                        s = v.text.rstrip('\n')
                        string += '    {}^\n'.format(''.join([(c.isspace() and c or ' ') for c in s[:min(len(s), v.offset) - 1].lstrip()]))
                    if t.__module__ not in ('__main__', 'builtins',):
                        string += t.__module__ + '.'
                    string += t.__qualname__
                    string += ': ' + (v.msg or '<no detail available>')
                else:
                    with frames(make=frames.traceback(v)) as f:
                        if f.has():
                            string += '  File "{}", line {}, in {}\n'.format(f[0].f_code.co_filename, f[0].f_lineno, f[0].f_code.co_name)
                            string += '    {}\n'.format(linecache.getline(f[0].f_code.co_filename, f[0].f_lineno).strip())
                    if t.__module__ not in ('__main__', 'builtins',):
                        string += t.__module__ + '.'
                    string += t.__qualname__
                    try:
                        s = str(v)
                    except BaseException:
                        s = '<unprintable %s object>' % t.__name__
                    if s:
                        string += ': ' + s
                if string:
                    strings.append(string)
            except BaseException:
                pass
        return start + '\n\n'.join(strings) + end

    def __init__(self, *exceptions):
        super().__init__(MultiException.join(*exceptions))


class EnterException(MultiException):
    pass


class ExitException(MultiException):
    pass


class Arguments:
    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = dict(kwargs)

    # 追加不定长参数
    def extend(self, *args):
        self.args.extend(args)
        return self

    # 更新关键字参数
    def update(self, **kwargs):
        self.kwargs.update(kwargs)
        return self

    def __call__(self, call):
        return call(*self.args, **self.kwargs)

    @staticmethod
    def make(generics):
        if isinstance(generics, Arguments):
            return generics
        elif isinstance(generics, tuple):
            return Arguments(*generics)
        elif isinstance(generics, dict):
            return Arguments(**generics)
        elif isinstance(generics, collections.Iterable):
            arguments = Arguments()
            for g in generics:
                if isinstance(g, tuple):
                    arguments.extend(*g)
                elif isinstance(g, dict):
                    arguments.update(**g)
            return arguments
        raise TypeError
