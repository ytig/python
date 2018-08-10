#!/usr/local/bin/python3
import inspect
from kit import unique, search, hasvar, getvar, setvar, frames, scope, depth
from decorator import Lock


# 定义类型
def define(__class__, __new__=None):
    context = scope(pattern=r'__new__', back=1)
    assert 'args' in context and 'kwargs' in context
    args = context['args']
    kwargs = context['kwargs']
    assert __class__ is not None and __class__ is context['freevars'].get('__class__')
    with Lock(__class__):
        assert hasvar(__class__, '__unique__') or setvar(__class__, '__unique__', unique())
        __unique__ = getvar(__class__, '__unique__')
    if not callable(__new__):
        __new__ = super(__class__, args[0]).__new__
    namespace = args[3]

    def function(func, find=lambda f: f, name=''):
        assert callable(func)
        isgeneratorfunction = inspect.isgeneratorfunction(func)
        if key in namespace:
            def base(v=namespace[key]):
                f = find(v)
                assert callable(f)
                assert inspect.isgeneratorfunction(f) == isgeneratorfunction
                return f
        else:
            def base(k=key):
                f = None
                for b in search(lambda cls: cls.__bases__).depth(*ret.__bases__):
                    if hasvar(b, k):
                        f = find(getvar(b, k))
                        assert callable(f)
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
                for b in search(lambda cls: cls.__bases__).depth(*ret.__bases__):
                    if hasvar(b, k):
                        d = _wrapper.descriptor(getvar(b, k))
                        assert inspect.isdatadescriptor(d) == isdatadescriptor
                        break
                return d
        mark = '/'.join((__unique__, key, '',))
        return (_datadescriptor if isdatadescriptor else _descriptor)(desc, base, mark)
    for key, var, in dict(list(context['varnames'].items()) + list(context['cellvars'].items())).items():
        if isinstance(var, staticmethod):
            def find(v):
                assert isinstance(v, staticmethod)
                return v.__func__
            namespace[key] = staticmethod(function(var.__func__, find=find))
        elif isinstance(var, classmethod):
            def find(v):
                assert isinstance(v, classmethod)
                return v.__func__
            namespace[key] = classmethod(function(var.__func__, find=find))
        elif isinstance(var, property):
            if var.fget is not None:
                def find(v):
                    assert isinstance(v, property)
                    return v.fget
                fget = function(var.fget, find=find, name='fget')
            else:
                fget = None
            if var.fset is not None:
                def find(v):
                    assert isinstance(v, property)
                    return v.fset
                fset = function(var.fset, find=find, name='fset')
            else:
                fset = None
            if var.fdel is not None:
                def find(v):
                    assert isinstance(v, property)
                    return v.fdel
                fdel = function(var.fdel, find=find, name='fdel')
            else:
                fdel = None
            namespace[key] = property(fget=fget, fset=fset, fdel=fdel)
        elif inspect.isfunction(var):
            namespace[key] = function(var)
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
        def default(*args, **kwargs):
            assert d
            return d[0]
        if not update:
            args = None
            kwargs = None
        else:
            context = scope(back=1)
            assert 'args' in context and 'kwargs' in context
            args = context['args']
            kwargs = context['kwargs']
        return (_function.invoke, _generatorfunction.invoke,)[index - 0](args, kwargs, default)
    elif index in range(2, 5):
        def default(name):
            assert d
            b = hasattr(d[0], name)
            if not b and name == '__get__':
                return _wrapper.descriptor(d[0]).__get__
            assert b
            return getattr(d[0], name)
        if not update:
            args = None
            kwargs = None
        else:
            context = scope(back=1)
            assert 'args' in context and 'kwargs' in context
            args = context['args'][1:]
            kwargs = context['kwargs']
        return (_descriptor.get, _datadescriptor.set, _datadescriptor.delete,)[index - 2](args, kwargs, default)


# 函数
class _function:
    # 定义
    @staticmethod
    def define(func, base, mark):
        def wrapper(*args, **kwargs):
            mark
            if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
                return func(*args, **kwargs)
            else:
                _func = base()
                if callable(_func):
                    return _func(*args, **kwargs)
                else:
                    with frames(filter=lambda f: f.f_code is _function.f_codes[0]) as f:
                        assert f.has(0)
                        default = f[0].f_locals['default']
                    return default(*args, **kwargs)
        return wrapper

    # 调用
    @staticmethod
    def invoke(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _function.f_codes[1]) as f:
            assert f.has(0)
            base = f[0].f_locals['base']
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        _func = base()
        if callable(_func):
            return _func(*args, **kwargs)
        else:
            return default(*args, **kwargs)
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)


# 生成器函数
class _generatorfunction:
    # 定义
    @staticmethod
    def define(func, base, mark):
        def wrapper(*args, **kwargs):
            mark
            if not depth(equal=lambda f1, f2: f1.f_locals['mark'] == f2.f_locals['mark']):
                value = yield from func(*args, **kwargs)
                return value
            else:
                _func = base()
                if callable(_func):
                    value = yield from _func(*args, **kwargs)
                    return value
                else:
                    with frames(filter=lambda f: f.f_code is _generatorfunction.f_codes[0]) as f:
                        assert f.has(0)
                        default = f[0].f_locals['default']
                    value = yield from default(*args, **kwargs)
                    return value
        return wrapper

    # 调用
    @staticmethod
    def invoke(args, kwargs, default):
        with frames(filter=lambda f: f.f_code is _generatorfunction.f_codes[1]) as f:
            assert f.has(0)
            base = f[0].f_locals['base']
            if args is None or kwargs is None:
                args = f[0].f_locals['args']
                kwargs = f[0].f_locals['kwargs']
        _func = base()
        if callable(_func):
            value = yield from _func(*args, **kwargs)
            return value
        else:
            value = yield from default(*args, **kwargs)
            return value
    f_codes = (invoke.__func__.__code__, define.__func__(None, None, None).__code__,)


# 描述器
class _descriptor:
    # 定义
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
                return default('__get__')(*args, **kwargs)

    # 调用get
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
            return default('__get__')(*args, **kwargs)
    f_codes_get = (get.__func__.__code__, __get__.__code__,)


# 资料描述器
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
                return default('__set__')(*args, **kwargs)

    # 调用set
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
            return default('__set__')(*args, **kwargs)
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
                return default('__delete__')(*args, **kwargs)

    # 调用delete
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
            return default('__delete__')(*args, **kwargs)
    f_codes_delete = (delete.__func__.__code__, __delete__.__code__,)


# 包装器
class _wrapper:
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

    # 生成描述器
    @staticmethod
    def descriptor(desc):
        if hasattr(desc, '__set__') or hasattr(desc, '__delete__'):
            return _wrapper._datadescriptor(desc)
        else:
            return _wrapper._descriptor(desc)
