#!/usr/local/bin/python3
import inspect
from kit import unique, search, hasvar, getvar, setvar, frames, scope, depth
from decorator import Lock


# 定义类型
def define(__class__, __new__=None):
    context = scope(pattern=r'__new__', back=1)
    assert __class__ is not None and __class__ is context['freevars'].get('__class__')
    args = context.get('args')
    kwargs = context.get('kwargs')
    assert args is not None and kwargs is not None
    with Lock(__class__):
        assert hasvar(__class__, '__unique__') or setvar(__class__, '__unique__', unique())
        __unique__ = getvar(__class__, '__unique__')
    if not callable(__new__):
        __new__ = super(__class__, args[0]).__new__
    bases = tuple(search(lambda cls: cls.__bases__).depth(*args[2]))
    namespace = args[3]
    for key, var, in dict(list(context['varnames'].items()) + list(context['cellvars'].items())).items():
        def decorator(new, old, name=''):
            if inspect.isfunction(new):
                if not inspect.isfunction(old):
                    old = None
                mark = '/'.join((__unique__, key, name,))
                if inspect.isgeneratorfunction(new):
                    assert old is None or inspect.isgeneratorfunction(old)
                    return _generatorfunction.define(new, old, mark)
                else:
                    assert not inspect.isgeneratorfunction(old)
                    return _function.define(new, old, mark)
            else:
                return old
        _var = None
        if key in namespace:
            _var = namespace[key]
        else:
            for b in bases:
                if hasvar(b, key):
                    _var = getvar(b, key)
                    break
        if isinstance(var, staticmethod):
            var = var.__func__
            _var = _var.__func__ if isinstance(_var, staticmethod) else None
            namespace[key] = staticmethod(decorator(var, _var))
        elif isinstance(var, classmethod):
            var = var.__func__
            _var = _var.__func__ if isinstance(_var, classmethod) else None
            namespace[key] = classmethod(decorator(var, _var))
        elif isinstance(var, property):
            fget, fset, fdel, = (var.fget, var.fset, var.fdel,)
            _fget, _fset, _fdel, = (_var.fget, _var.fset, _var.fdel,) if isinstance(_var, property) else (None, None, None,)
            namespace[key] = property(fget=decorator(fget, _fget, name='fget'), fset=decorator(fset, _fset, name='fset'), fdel=decorator(fdel, _fdel, name='fdel'))
        elif inspect.isfunction(var):
            namespace[key] = decorator(var, _var)
        else:
            namespace[key] = var
    return __new__(*args, **kwargs)


# 原始调用
def invoke(*d, arguments=False):
    def default(*args, **kwargs):
        assert d
        return d[0]
    if not arguments:
        args = None
        kwargs = None
    else:
        context = scope(back=1)
        args = context.get('args')
        kwargs = context.get('kwargs')
    with frames(back=1) as f:
        assert f.has(0)
        isgeneratorfunction = bool(f[0].f_code.co_flags & 32)
    if isgeneratorfunction:
        return _generatorfunction.invoke(args, kwargs, default)
    else:
        return _function.invoke(args, kwargs, default)


class _function:
    @staticmethod
    def define(new, old, mark):
        def wrapper(*args, **kwargs):
            mark
            if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
                return new(*args, **kwargs)
            elif old is not None:
                return old(*args, **kwargs)
            else:
                with frames(filter=lambda f: f.f_code is _function.f_codes[0]) as f:
                    assert f.has(0)
                    default = f[0].f_locals['default']
                return default(*args, **kwargs)
        return wrapper

    @staticmethod
    def invoke(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _function.f_codes[1]) as f:
            assert f.has(0)
            old = f[0].f_locals['old']
            if args is None:
                args = f[0].f_locals['args']
            if kwargs is None:
                kwargs = f[0].f_locals['kwargs']
        if old is not None:
            return old(*args, **kwargs)
        else:
            return default(*args, **kwargs)
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)


class _generatorfunction:
    @staticmethod
    def define(new, old, mark):
        def wrapper(*args, **kwargs):
            mark
            if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
                value = yield from new(*args, **kwargs)
                return value
            elif old is not None:
                value = yield from old(*args, **kwargs)
                return value
            else:
                with frames(filter=lambda f: f.f_code is _generatorfunction.f_codes[0]) as f:
                    assert f.has(0)
                    default = f[0].f_locals['default']
                value = yield from default(*args, **kwargs)
                return value
        return wrapper

    @staticmethod
    def invoke(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _generatorfunction.f_codes[1]) as f:
            assert f.has(0)
            old = f[0].f_locals['old']
            if args is None:
                args = f[0].f_locals['args']
            if kwargs is None:
                kwargs = f[0].f_locals['kwargs']
        if old is not None:
            value = yield from old(*args, **kwargs)
            return value
        else:
            value = yield from default(*args, **kwargs)
            return value
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)
