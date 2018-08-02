#!/usr/local/bin/python3
import inspect
from kit import search, setvar, getvar, depth
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
                    if not depth():
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
            setvar(r.fget or r.fset or r.fdel, '__export__', property(fget=_exec()(r.fget) if r.fget else None, fset=_exec()(r.fset) if r.fset else None, fdel=_exec()(r.fdel) if r.fdel else None))
        return r

    @staticmethod
    def get(o):
        return getvar(o.fget or o.fset or o.fdel, '__export__')


class _function:
    @staticmethod
    def set(o, b):
        r = _except()(o)
        if b:
            setvar(r, '__export__', _exec()(r))
        return r

    @staticmethod
    def get(o):
        return getvar(o, '__export__')


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
        if name:
            if name in self.__getting:
                return self.__getting[name](self.__setting[name] if name in self.__setting else None)
            else:
                return None
        else:
            g = {}
            for n in self.__getting:
                if not n:
                    continue
                g[n] = self.getting(name=n)
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

            def sum(data, total=len(mems), sync=t <= 0):
                form = {}
                success = len(data)
                if success > 0:
                    form['success'] = {}
                    for r in data:
                        r = str(r)
                        if r not in form['success']:
                            form['success'][r] = 1
                        else:
                            form['success'][r] += 1
                failure = total - success
                if failure > 0:
                    form['failure'] = {}
                    if sync:
                        form['failure']['raise'] = 1
                        if failure > 1:
                            form['failure']['pass'] = failure - 1
                    else:
                        form['failure']['raise'] = failure
                return str(form)

            class _list(list):
                def __str__(self):
                    return sum(self)

                def __repr__(self):
                    return sum(self)
            if t <= 0:
                ret = _list()
                try:
                    for mem in mems:
                        ret.append(cpu(mem))
                except BaseException:
                    pass
                return ret
            else:
                return _list(Tree(cpu, *mems, log=None).plant(t=t))


class _metaclass(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        searcher = search(lambda cls: [b for b in cls.__bases__ if b is not object])
        if _baseclass in bases and len(bases) == 1:
            final = set()
            final.update(namespace.keys())
            for b in searcher.depth(*bases):
                final.update(vars(b).keys())
            override = set()
            base = namespace['__cls__']
            name = base.__name__
            for b in searcher.depth(base):
                for k, v in vars(b).items():
                    if k not in override:
                        override.add(k)
                        if isinstance(v, staticmethod):
                            v = _staticmethod.get(v)
                        elif isinstance(v, classmethod):
                            v = _classmethod.get(v)
                        elif isinstance(v, property):
                            v = _property.get(v)
                        elif inspect.isfunction(v):
                            v = _function.get(v)
                        else:
                            v = None
                        if v:
                            if k in final:
                                raise Exception('cannot export keyword ' + k + '.')
                            namespace[k] = v
            return super().__new__(mcls, name, bases, namespace, **kwargs)
        else:
            bases = tuple([getvar(b, '__cls__', d=b) if issubclass(b, _baseclass) else b for b in bases])
            return type.__new__(type, name, bases, namespace, **kwargs)


class _class:
    @staticmethod
    def set(o):
        class classes(_baseclass, metaclass=_metaclass):
            __cls__ = o  # 原类

            def __init__(self, *objects, **setting):
                for obj in objects:
                    if obj.__class__ is not __class__.__cls__:
                        name = str(getattr(obj.__class__, '__name__', None))
                        raise Exception('cannot append instance of ' + name + '.')
                super().__init__(*objects, **setting)
        return classes

    @staticmethod
    def get(o):
        while inspect.isclass(o) and issubclass(o, _baseclass):
            o = getvar(o, '__cls__')
        return o
