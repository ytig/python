#!/usr/local/bin/python3
import inspect
from kit import unique, hasvar, getvar, setvar, frames, scope, depth
from decorator import Lock


# 定义类型
def define(__class__, __new__=None):
    context = scope(pattern=r'__new__', back=1)
    args = context['args']
    kwargs = context['kwargs']
    assert __class__ is not None and __class__ is context['freevars'].get('__class__')
    with Lock(__class__):
        assert hasvar(__class__, '__unique__') or setvar(__class__, '__unique__', unique())
        __unique__ = getvar(__class__, '__unique__')
    if not callable(__new__):
        __new__ = super(__class__, __class__).__new__
    namespace = args[3]

    def function(func, find, name=''):
        isgeneratorfunction = inspect.isgeneratorfunction(func)
        if key in namespace:
            def base(v=namespace[key]):
                f = find(v)
                assert inspect.isgeneratorfunction(f) == isgeneratorfunction
                return f
        else:
            def base(k=key):
                f = None
                for b in type.mro(ret)[1:]:
                    if hasvar(b, k):
                        f = find(_wrapper.function(getvar(b, k)))
                        assert inspect.isgeneratorfunction(f) == isgeneratorfunction
                        break
                return f
        mark = '/'.join((__unique__, key, name,))
        return (_generatorfunction if isgeneratorfunction else _function).define(func, base, mark)

    def descriptor(desc):
        desc = _wrapper.descriptor(desc)
        isdatadescriptor = inspect.isdatadescriptor(desc)
        if key in namespace:
            def base(v=namespace[key]):
                d = _wrapper.descriptor(v)
                assert inspect.isdatadescriptor(d) == isdatadescriptor
                return d
        else:
            def base(k=key):
                d = None
                for b in type.mro(ret)[1:]:
                    if hasvar(b, k):
                        d = _wrapper.descriptor(getvar(b, k))
                        assert inspect.isdatadescriptor(d) == isdatadescriptor
                        break
                return d
        mark = '/'.join((__unique__, key, '',))
        return (_datadescriptor if isdatadescriptor else _descriptor)(desc, base, mark)
    for key, var, in dict(context['varnames'], **context['cellvars']).items():
        if isinstance(var, staticmethod):
            if callable(var.__func__):
                def find(v):
                    assert isinstance(v, staticmethod) and callable(v.__func__)
                    return v.__func__
                __func__ = function(var.__func__, find)
            else:
                __func__ = None
            namespace[key] = staticmethod(__func__)
        elif isinstance(var, classmethod):
            if callable(var.__func__):
                def find(v):
                    assert isinstance(v, classmethod) and callable(v.__func__)
                    return v.__func__
                __func__ = function(var.__func__, find)
            else:
                __func__ = None
            namespace[key] = classmethod(__func__)
        elif isinstance(var, property):
            if callable(var.fget):
                def find(v):
                    assert isinstance(v, property) and callable(v.fget)
                    return v.fget
                fget = function(var.fget, find, name='fget')
            else:
                fget = None
            if callable(var.fset):
                def find(v):
                    assert isinstance(v, property) and callable(v.fset)
                    return v.fset
                fset = function(var.fset, find, name='fset')
            else:
                fset = None
            if callable(var.fdel):
                def find(v):
                    assert isinstance(v, property) and callable(v.fdel)
                    return v.fdel
                fdel = function(var.fdel, find, name='fdel')
            else:
                fdel = None
            namespace[key] = property(fget=fget, fset=fset, fdel=fdel)
        elif inspect.isfunction(var):
            def find(v):
                assert callable(v)
                return v
            namespace[key] = function(var, find)
        else:
            namespace[key] = descriptor(var)
    ret = __new__(*args, **kwargs)
    return ret


# 原始调用
def invoke(*d, update=False):
    codes = (_function.f_codes[1], _generatorfunction.f_codes[1], _descriptor.f_codes_get[1], _datadescriptor.f_codes_set[1], _datadescriptor.f_codes_delete[1],)
    with frames(filter=lambda f: f.f_code in codes) as f:
        assert f.has(0)
        index = codes.index(f[0].f_code)
    if index in range(0, 2):
        index -= 0

        def default(*args, **kwargs):
            assert d
            return d[0]
        if not update:
            args = None
            kwargs = None
        else:
            context = scope(pattern=r'', back=1)
            args = context['args']
            kwargs = context['kwargs']
        return (_function.invoke, _generatorfunction.invoke,)[index](args, kwargs, default)
    elif index in range(2, 5):
        index -= 2

        def default(*args, **kwargs):
            name = args[0]
            args = args[1:]
            assert d
            b = hasattr(d[0], name)
            if not b and name == '__get__':
                return d[0]
            assert b
            return getattr(d[0], name)(*args, **kwargs)
        if not update:
            args = None
            kwargs = None
        else:
            context = scope(pattern=(r'__get__', r'__set__', r'__delete__',)[index], back=1)
            assert context['args']
            args = context['args'][1:]
            kwargs = context['kwargs']
        return (_descriptor.get, _datadescriptor.set, _datadescriptor.delete,)[index](args, kwargs, default)


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
        _func = base()
        if _func is not None:
            return _func(*args, **kwargs)
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
        _func = base()
        if _func is not None:
            value = yield from _func(*args, **kwargs)
            return value
        else:
            value = yield from default(*args, **kwargs)
            return value
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)


class _descriptor:
    def __init__(self, desc, base, mark):
        self.desc = desc
        self.base = base
        self.mark = mark

    def __get__(self, *args, **kwargs):
        if not depth(equal=lambda f1, f2: f1.f_locals['self'].mark == f2.f_locals['self'].mark):
            return self.desc.__get__(*args, **kwargs)
        else:
            _desc = self.base()
            if _desc is not None:
                return _desc.__get__(*args, **kwargs)
            else:
                with frames(filter=lambda f: f.f_code is _descriptor.f_codes_get[0]) as f:
                    assert f.has(0)
                    default = f[0].f_locals['default']
                return default('__get__', *args, **kwargs)

    @staticmethod
    def get(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _descriptor.f_codes_get[1]) as f:
            assert f.has(0)
            base = f[0].f_locals['self'].base
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        _desc = base()
        if _desc is not None:
            return _desc.__get__(*args, **kwargs)
        else:
            return default('__get__', *args, **kwargs)
    f_codes_get = (get.__func__.__code__, __get__.__code__,)


class _datadescriptor(_descriptor):
    def __set__(self, *args, **kwargs):
        if not depth(equal=lambda f1, f2: f1.f_locals['self'].mark == f2.f_locals['self'].mark):
            return self.desc.__set__(*args, **kwargs)
        else:
            _desc = self.base()
            if _desc is not None:
                return _desc.__set__(*args, **kwargs)
            else:
                with frames(filter=lambda f: f.f_code is _datadescriptor.f_codes_set[0]) as f:
                    assert f.has(0)
                    default = f[0].f_locals['default']
                return default('__set__', *args, **kwargs)

    @staticmethod
    def set(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _datadescriptor.f_codes_set[1]) as f:
            assert f.has(0)
            base = f[0].f_locals['self'].base
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        _desc = base()
        if _desc is not None:
            return _desc.__set__(*args, **kwargs)
        else:
            return default('__set__', *args, **kwargs)
    f_codes_set = (set.__func__.__code__, __set__.__code__,)

    def __delete__(self, *args, **kwargs):
        if not depth(equal=lambda f1, f2: f1.f_locals['self'].mark == f2.f_locals['self'].mark):
            return self.desc.__delete__(*args, **kwargs)
        else:
            _desc = self.base()
            if _desc is not None:
                return _desc.__delete__(*args, **kwargs)
            else:
                with frames(filter=lambda f: f.f_code is _datadescriptor.f_codes_delete[0]) as f:
                    assert f.has(0)
                    default = f[0].f_locals['default']
                return default('__delete__', *args, **kwargs)

    @staticmethod
    def delete(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _datadescriptor.f_codes_delete[1]) as f:
            assert f.has(0)
            base = f[0].f_locals['self'].base
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        _desc = base()
        if _desc is not None:
            return _desc.__delete__(*args, **kwargs)
        else:
            return default('__delete__', *args, **kwargs)
    f_codes_delete = (delete.__func__.__code__, __delete__.__code__,)


class _wrapper:
    @staticmethod
    def __new__(*args, **kwargs):
        return object.__dict__['__new__'](args[0])

    def __init__(self, *args, **kwargs):
        return object.__dict__['__init__'](self, *args, **kwargs)

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        return object.__dict__['__init_subclass__'](cls, *args, **kwargs)

    @classmethod
    def __subclasshook__(cls, *args, **kwargs):
        return object.__dict__['__subclasshook__'](cls, *args, **kwargs)

    @staticmethod
    def function(func):
        for key in ('__new__', '__init__', '__init_subclass__', '__subclasshook__',):
            if func is object.__dict__[key]:
                return _wrapper.__dict__[key]
        return func

    class _descriptor:
        def __init__(self, desc):
            self.desc = desc

        def __get__(self, *args, **kwargs):
            return self.desc.__get__(*args, **kwargs) if hasattr(self.desc, '__get__') else self.desc

    class _datadescriptor(_descriptor):
        def __set__(self, *args, **kwargs):
            assert hasattr(self.desc, '__set__')
            return self.desc.__set__(*args, **kwargs)

        def __delete__(self, *args, **kwargs):
            assert hasattr(self.desc, '__delete__')
            return self.desc.__delete__(*args, **kwargs)

    @staticmethod
    def descriptor(desc):
        if hasattr(desc, '__set__') or hasattr(desc, '__delete__'):
            return _wrapper._datadescriptor(desc)
        else:
            return _wrapper._descriptor(desc)
