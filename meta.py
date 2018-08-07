#!/usr/local/bin/python3
import inspect
from kit import unique, search, hasvar, getvar, setvar, frames, getargs, depth
from decorator import Lock


# 定义类型
def define(__class__, __new__=None):
    with frames(back=1) as f:
        assert f.has(0)
        assert '__class__' in f[0].f_code.co_freevars and __class__ is f[0].f_locals.get('__class__')
        args, kwargs, keywords, = getargs(pattern=r'__new__', back=1)
        assert None not in (args, kwargs, keywords,)
        with Lock(__class__):
            assert hasvar(__class__, '__unique__') or setvar(__class__, '__unique__', unique())
            __unique__ = getvar(__class__, '__unique__')
        if not callable(__new__):
            __new__ = super(__class__, args[0]).__new__
        bases = tuple(search(lambda cls: cls.__bases__).depth(*args[2]))
        namespace = args[3]
        for key in f[0].f_code.co_varnames + f[0].f_code.co_cellvars:
            if key in keywords or key not in f[0].f_locals:
                continue

            def decorator(new, old, name=''):
                if inspect.isfunction(new):
                    mark = '/'.join((__unique__, key, name,))
                    if inspect.isgeneratorfunction(new):
                        if not inspect.isgeneratorfunction(old):
                            old = None
                        return _generatorfunction.define(new, old, mark)
                    else:
                        if not inspect.isfunction(old):
                            old = None
                        return _function.define(new, old, mark)
                else:
                    return old
            var = f[0].f_locals[key]
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
def invoke(*d):
    with frames(back=1) as f:
        assert f.has(0)
        isgeneratorfunction = bool(f[0].f_code.co_flags & 32)
    if isgeneratorfunction:
        return _generatorfunction.invoke(*d)
    else:
        return _function.invoke(*d)


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
                with frames(filter=lambda f: f.f_code is __class__.f_codes[0]) as f:
                    assert f.has(0)
                    d = f[0].f_locals['d']
                assert d
                return d[0]
        return wrapper

    @staticmethod
    def invoke(*d):
        with frames(filter=lambda f: f.f_code is __class__.f_codes[1]) as f:
            assert f.has(0)
            old = f[0].f_locals['old']
            args = f[0].f_locals['args']
            kwargs = f[0].f_locals['kwargs']
        if old is not None:
            return old(*args, **kwargs)
        else:
            assert d
            return d[0]
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
                with frames(filter=lambda f: f.f_code is __class__.f_codes[0]) as f:
                    assert f.has(0)
                    d = f[0].f_locals['d']
                assert d
                value = yield from d[0]
                return value
        return wrapper

    @staticmethod
    def invoke(*d):
        with frames(filter=lambda f: f.f_code is __class__.f_codes[1]) as f:
            assert f.has(0)
            old = f[0].f_locals['old']
            args = f[0].f_locals['args']
            kwargs = f[0].f_locals['kwargs']
        if old is not None:
            value = yield from old(*args, **kwargs)
            return value
        else:
            assert d
            value = yield from d[0]
            return value
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)
