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
    namespace = args[3]

    def function(func, find, name=''):
        assert inspect.isfunction(func)
        isgeneratorfunction = inspect.isgeneratorfunction(func)
        if key in namespace:
            def base(v=namespace[key]):
                f = find(v)
                assert inspect.isfunction(f)
                assert inspect.isgeneratorfunction(f) == isgeneratorfunction
                return f
        else:
            def base(k=key):
                f = None
                for b in search(lambda cls: cls.__bases__).depth(*ret.__bases__):
                    if hasvar(b, k):
                        f = find(getvar(b, k))
                        assert inspect.isfunction(f)
                        assert inspect.isgeneratorfunction(f) == isgeneratorfunction
                        break
                return f
        mark = '/'.join((__unique__, key, name,))
        return (_generatorfunction if isgeneratorfunction else _function).define(func, base, mark)
    for key, var, in dict(list(context['varnames'].items()) + list(context['cellvars'].items())).items():
        if isinstance(var, staticmethod):
            def find(v):
                assert isinstance(v, staticmethod)
                return v.__func__
            namespace[key] = staticmethod(function(var.__func__, find))
        elif isinstance(var, classmethod):
            def find(v):
                assert isinstance(v, classmethod)
                return v.__func__
            namespace[key] = classmethod(function(var.__func__, find))
        elif isinstance(var, property):
            if var.fget is not None:
                def find(v):
                    assert isinstance(v, property)
                    return v.fget
                fget = function(var.fget, find, name='fget')
            else:
                fget = None
            if var.fset is not None:
                def find(v):
                    assert isinstance(v, property)
                    return v.fset
                fset = function(var.fset, find, name='fset')
            else:
                fset = None
            if var.fdel is not None:
                def find(v):
                    assert isinstance(v, property)
                    return v.fdel
                fdel = function(var.fdel, find, name='fdel')
            else:
                fdel = None
            namespace[key] = property(fget=fget, fset=fset, fdel=fdel)
        elif inspect.isfunction(var):
            def find(v):
                return v
            namespace[key] = function(var, find)
    ret = __new__(*args, **kwargs)
    return ret


# 原始调用
def invoke(*d, update=False):
    def default(*args, **kwargs):
        assert d
        return d[0]
    if not update:
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
    def define(func, base, mark):
        def wrapper(*args, **kwargs):
            mark
            if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
                return func(*args, **kwargs)
            else:
                _func = base()
                if _func is not None:
                    return _func(*args, **kwargs)
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
            base = f[0].f_locals['base']
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        func = base()
        if func is not None:
            return func(*args, **kwargs)
        else:
            return default(*args, **kwargs)
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)


class _generatorfunction:
    @staticmethod
    def define(func, base, mark):
        def wrapper(*args, **kwargs):
            mark
            if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
                value = yield from func(*args, **kwargs)
                return value
            else:
                _func = base()
                if _func is not None:
                    value = yield from _func(*args, **kwargs)
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
            base = f[0].f_locals['base']
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        func = base()
        if func is not None:
            value = yield from func(*args, **kwargs)
            return value
        else:
            value = yield from default(*args, **kwargs)
            return value
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)
