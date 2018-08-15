#!/usr/local/bin/python3
import inspect
from kit import hasvar, getvar, setvar, depth
from decorator import Lock, ilock
from task import Tree


# 导出
def export(generics):
    """
    generics must be staticmethod, classmethod, property, function, class.
    staticmethod, classmethod: replace a raised, export original to classes.
    property, function: replace an excepted, exception will be catch to __except__, export replaced as a classes forin type.
    class: replace a classes, the original class is __cls__, setting and getting are used to define configure.

    about classes configure.
    t: thread count, default 0.
    """
    if isinstance(generics, staticmethod):
        return _staticmethod.set(generics, True)
    elif isinstance(generics, classmethod):
        return _classmethod.set(generics, True)
    elif isinstance(generics, property):
        return _property.set(generics, True)
    elif inspect.isfunction(generics):
        return _function.set(generics, True)
    elif inspect.isclass(generics):
        return _class.set(generics)


# 非导出
def deport(generics):
    """
    generics must be staticmethod, classmethod, property, function, class.
    staticmethod, classmethod: deprecated.
    property, function: replace an excepted, exception will be catch to __except__.
    class: find the original class.
    """
    if isinstance(generics, staticmethod):
        return _staticmethod.set(generics, False)
    elif isinstance(generics, classmethod):
        return _classmethod.set(generics, False)
    elif isinstance(generics, property):
        return _property.set(generics, False)
    elif inspect.isfunction(generics):
        return _function.set(generics, False)
    elif inspect.isclass(generics):
        return _class.get(generics)


class _staticmethod:
    @staticmethod
    def set(o, b):
        @staticmethod
        def r(*args, **kwargs):
            raise Exception('staticmethod has been exported.')
        if b:
            setvar(r, '__export__', o)
        return r

    @staticmethod
    def get(o):
        return getvar(o, '__export__')


class _classmethod:
    @staticmethod
    def set(o, b):
        @classmethod
        def r(*args, **kwargs):
            raise Exception('classmethod has been exported.')
        if b:
            setvar(r, '__export__', o)
        return r

    @staticmethod
    def get(o):
        return getvar(o, '__export__')


def _except(fn='__except__'):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            try:
                return function(self, *args, **kwargs)
            except BaseException as e:
                try:
                    if not depth(equal=lambda f1, f2: f1.f_locals['self'] is f2.f_locals['self']):
                        if hasattr(self, fn):
                            getattr(self, fn)(e)
                except BaseException:
                    pass
                raise
        return wrapper
    return decorator


def _exec(fn='__exec__'):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, fn):
                return getattr(self, fn)(function, *args, **kwargs)
        return wrapper
    return decorator


class _property:
    @staticmethod
    def set(o, b):
        r = property(fget=_except()(o.fget) if o.fget else None, fset=_except()(o.fset) if o.fset else None, fdel=_except()(o.fdel) if o.fdel else None)
        if b:
            setvar(r.fget or r.fset or r.fdel, '__export__', True)
        return r

    @staticmethod
    def get(o):
        return property(fget=_exec()(o.fget) if o.fget else None, fset=_exec()(o.fset) if o.fset else None, fdel=_exec()(o.fdel) if o.fdel else None) if getvar(o.fget or o.fset or o.fdel, '__export__') else None


class _function:
    @staticmethod
    def set(o, b):
        r = _except()(o)
        if b:
            setvar(r, '__export__', True)
        return r

    @staticmethod
    def get(o):
        return _exec()(o) if getvar(o, '__export__') else None


class _list(list):
    def __init__(self, total, sync):
        super().__init__()
        self.__t = total
        self.__s = sync

    def __ret__(self):
        form = {}
        success = len(self)
        if success > 0:
            form['success'] = {}
            for r in self:
                r = str(r)
                if r not in form['success']:
                    form['success'][r] = 1
                else:
                    form['success'][r] += 1
        failure = self.__t - success
        if failure > 0:
            form['failure'] = {}
            if self.__s:
                form['failure']['raise'] = 1
                if failure > 1:
                    form['failure']['pass'] = failure - 1
            else:
                form['failure']['raise'] = failure
        return str(form)

    def __str__(self):
        return self.__ret__()

    def __repr__(self):
        return self.__ret__()


class _baseclass:
    def __init__(self, *objects, **setting):
        self.__objects = list(objects)
        self.__setting = dict(setting)
        self.__getting = {
            't': lambda t: t if isinstance(t, int) and t >= 0 else 0,
        }

    @ilock()
    def __len__(self):
        return len(self.__objects)

    # 写设置
    @ilock()
    def setting(self, **setting):
        self.__setting.update(setting)
        return self

    # 读设置
    @ilock()
    def getting(self, name=None):
        if name is not None:
            if name in self.__getting:
                return self.__getting[name](self.__setting.get(name))
            else:
                return None
        else:
            g = {}
            for n in self.__getting:
                g[n] = self.__getting[n](self.__setting.get(n))
            return g

    def __exec__(self, *args, **kwargs):
        if args:
            function = args[0]
            args = args[1:]
            with Lock(self):
                mems = self.__objects.copy()
                t = self.getting(name='t')

            def cpu(mem):
                try:
                    return function(mem, *args, **kwargs)
                except BaseException:
                    with Lock(self):
                        if mem in self.__objects:
                            self.__objects.remove(mem)
                    raise
            ret = _list(len(mems), t <= 0)
            if t <= 0:
                try:
                    for mem in mems:
                        ret.append(cpu(mem))
                except BaseException:
                    pass
            else:
                ret.extend(Tree(cpu, *mems, log=None).plant(t=t))
            return ret


class _metaclass(type):
    @staticmethod
    def __new__(mcls, name, bases, namespace, **kwargs):
        if 'baseclass' in kwargs:
            namespace['__cls__'] = kwargs['baseclass']
            del kwargs['baseclass']

            def __init__(self, *objects, **setting):
                for obj in objects:
                    assert type(obj) is __class__.__cls__
                return super(__class__, self).__init__(*objects, **setting)
            namespace['__init__'] = __init__

            def __getattribute__(self, name):
                for c in type(self).__cls__.__mro__:
                    if hasvar(c, name):
                        var = getvar(c, name)
                        if isinstance(var, property):
                            return _property.get(var).__get__(self, type(self))
                        break
                try:
                    return super(__class__, self).__getattribute__(name)
                except AttributeError:
                    for c in type(self).__cls__.__mro__:
                        if hasvar(c, name):
                            var = getvar(c, name)
                            if inspect.isfunction(var):
                                return _function.get(var).__get__(self, type(self))
                            break
                    raise
            namespace['__getattribute__'] = __getattribute__

            def __setattr__(self, name, value):
                for c in type(self).__cls__.__mro__:
                    if hasvar(c, name):
                        var = getvar(c, name)
                        if isinstance(var, property):
                            return _property.get(var).__set__(self, value)
                        break
                return super(__class__, self).__setattr__(name, value)
            namespace['__setattr__'] = __setattr__

            def __delattr__(self, name):
                for c in type(self).__cls__.__mro__:
                    if hasvar(c, name):
                        var = getvar(c, name)
                        if isinstance(var, property):
                            return _property.get(var).__delete__(self)
                        break
                return super(__class__, self).__delattr__(name)
            namespace['__delattr__'] = __delattr__
            __class__ = type.__new__(mcls, name, (_baseclass,), namespace, **kwargs)
            return __class__
        else:
            bases = list(bases)
            for i in range(len(bases)):
                while isinstance(bases[i], _metaclass):
                    bases[i] = bases[i].__cls__
            return type(name, tuple(bases), namespace, **kwargs)

    def __getattr__(cls, name):
        for c in cls.__cls__.__mro__:
            if hasvar(c, name):
                var = getvar(c, name)
                if isinstance(var, staticmethod):
                    return _staticmethod.get(var).__get__(None, cls)
                elif isinstance(var, classmethod):
                    return _classmethod.get(var).__get__(None, cls)
                break
        raise AttributeError


class _class:
    @staticmethod
    def set(o):
        class classes(metaclass=_metaclass, baseclass=o):
            pass
        return classes

    @staticmethod
    def get(o):
        while inspect.isclass(o) and isinstance(o, _metaclass):
            o = o.__cls__
        return o
