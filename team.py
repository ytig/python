#!/usr/local/bin/python3
import inspect
from decorator import Lock, synchronized
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
            __class__._set(r, '__export__', o)
        return r

    @staticmethod
    def _set(obj, name, value):
        setattr(obj, name, value)

    @staticmethod
    def get(o):
        return __class__._get(o, '__export__', None)

    @staticmethod
    def _get(obj, name, default):
        return getattr(obj, name, default)


class _classmethod:
    @staticmethod
    def set(o, b):
        @classmethod
        def r(*args, **kwargs):
            raise Exception('classmethod has been exported.')
        if b:
            __class__._set(r, '__export__', o)
        return r

    @staticmethod
    def _set(obj, name, value):
        setattr(obj, name, value)

    @staticmethod
    def get(o):
        return __class__._get(o, '__export__', None)

    @staticmethod
    def _get(obj, name, default):
        return getattr(obj, name, default)


def _except(fn='__except__'):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            try:
                return function(self, *args, **kwargs)
            except BaseException as e:
                try:
                    cf = inspect.currentframe()
                    fb = cf.f_back
                    while fb:
                        if cf.f_code is fb.f_code:
                            break
                        fb = fb.f_back
                    if not fb:
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
            __class__._set(r, '__export__', property(fget=_exec()(r.fget) if r.fget else None, fset=_exec()(r.fset) if r.fset else None, fdel=_exec()(r.fdel) if r.fdel else None))
        return r

    @staticmethod
    def _set(obj, name, value):
        if obj.fget:
            obj = obj.fget
        elif obj.fset:
            obj = obj.fset
        elif obj.fdel:
            obj = obj.fdel
        else:
            return
        setattr(obj, name, value)

    @staticmethod
    def get(o):
        return __class__._get(o, '__export__', None)

    @staticmethod
    def _get(obj, name, default):
        if obj.fget:
            obj = obj.fget
        elif obj.fset:
            obj = obj.fset
        elif obj.fdel:
            obj = obj.fdel
        else:
            return default
        return getattr(obj, name, default)


class _function:
    @staticmethod
    def set(o, b):
        r = _except()(o)
        if b:
            __class__._set(r, '__export__', _exec()(r))
        return r

    @staticmethod
    def _set(obj, name, value):
        setattr(obj, name, value)

    @staticmethod
    def get(o):
        return __class__._get(o, '__export__', None)

    @staticmethod
    def _get(obj, name, default):
        return getattr(obj, name, default)


class _base:
    def __init__(self, *objects, **setting):
        self.__objects = list(objects)
        self.__setting = dict(setting)
        self.__getting = {
            't': lambda t: t if isinstance(t, int) and t >= 0 else 0,
        }

    @synchronized()
    def __len__(self):
        return len(self.__objects)

    # 写设置
    @synchronized()
    def setting(self, **setting):
        self.__setting.update(setting)
        return self

    # 读设置
    @synchronized()
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
        final = []
        final.extend(namespace.keys())
        for b in bases:
            while b is not object:
                final.extend(vars(b).keys())
                b = b.__base__
        override = []
        base = namespace['__cls__']
        name = base.__name__
        while base is not object:
            for k, v in vars(base).items():
                if k not in override:
                    override.append(k)
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
            base = base.__base__
        return super().__new__(mcls, name, bases, namespace, **kwargs)


class _class:
    @staticmethod
    def set(o):
        class classes(_base, metaclass=_metaclass):
            __cls__ = o

            def __init__(self, *objects, **setting):
                for obj in objects:
                    c = getattr(obj, '__class__', None)
                    if c is not __class__.__cls__:
                        n = getattr(c, '__name__', None)
                        raise Exception('cannot append instance of ' + str(n) + '.')
                super().__init__(*objects, **setting)
        return classes

    @staticmethod
    def get(o):
        while inspect.isclass(o) and issubclass(o, _base):
            o = getattr(o, '__cls__', None)
        return o
