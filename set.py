#!/usr/local/bin/python3
import inspect
from decorator import Lock, synchronized
from task import Tree


# 执行
def _exec(cpu, *mems, t=0):
    total = len(mems)

    def outline(rets):
        ret = {}
        success = len(rets)
        if success > 0:
            ret['success'] = {}
            for r in rets:
                r = str(r)
                if r not in ret['success']:
                    ret['success'][r] = 1
                else:
                    ret['success'][r] += 1
        failure = total - success
        if failure > 0:
            ret['failure'] = {}
            if t == 0:
                ret['failure']['raise'] = 1
                if failure > 1:
                    ret['failure']['pass'] = failure - 1
            else:
                ret['failure']['raise'] = failure
        return str(ret)

    class List(list):
        def __str__(self):
            return outline(self)

        def __repr__(self):
            return outline(self)
    if isinstance(t, int) and t > 0:
        return List(Tree(cpu, *mems, log=None).plant(t=t))
    else:
        ret = List()
        try:
            for mem in mems:
                ret.append(cpu(mem))
        except BaseException:
            pass
        return ret


# 捕获
def _except(fn):
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


# 导出
def export(generics):
    """
    generics must be class, staticmethod, classmethod, function.
    class: export Set class, the original class is Set.__cls__.
    staticmethod: not useful.
    classmethod: export Set class constructor.
    function: export Set class forinmethod which would not raise any exception, exception will be catch to __except__.

    Set.setting and Set.getting are used to define configure.
    t: thread count, default 0.
    """
    if inspect.isclass(generics):
        def imports(l):
            def decorator(function):
                def wrapper(self, *args, **kwargs):
                    return self.exec(function, *args, **kwargs)
                return wrapper
            cls = l['__cls__']
            a = list(l.keys())
            b = []
            while cls:
                for k, v in vars(cls).items():
                    if k not in b:
                        b.append(k)
                        m = None
                        if isinstance(v, staticmethod):
                            f = getattr(v.__func__, '__export__', None)
                            if callable(f):
                                m = staticmethod(f)
                        elif isinstance(v, classmethod):
                            f = getattr(v.__func__, '__export__', None)
                            if callable(f):
                                m = classmethod(f)
                        elif inspect.isfunction(v):
                            f = getattr(v, '__export__', None)
                            if callable(f):
                                m = decorator(f)
                        if m:
                            if k in a:
                                raise Exception('cannot export keyword of Set.')
                            l[k] = m
                cls = cls.__base__

        class Set:
            __cls__ = generics  # 原类

            def __init__(self, *objects, **setting):
                self.__objects = []
                for obj in objects:
                    if isinstance(obj, generics):
                        self.__objects.append(obj)
                self.__setting = {}
                self.__getting = {
                    't': lambda t: t if isinstance(t, int) and t >= 0 else 0,
                }
                self.setting(**setting)

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
                        if n:
                            g[n] = self.getting(name=n)
                    return g

            def exec(self, *args, **kwargs):
                if args:
                    function = args[0]
                    args = args[1:]
                    with Lock(self):
                        mems = self.__objects.copy()
                        t = self.getting(name='t')

                    def cpu(obj):
                        try:
                            return function(obj, *args, **kwargs)
                        except BaseException as e:
                            with Lock(self):
                                if obj in self.__objects:
                                    self.__objects.remove(obj)
                            raise
                    return _exec(cpu, *mems, t=t)
            imports(locals())
        return Set
    elif isinstance(generics, staticmethod):
        def sm(*args, **kwargs):
            raise Exception('staticmethod has been exported.')
        sm.__export__ = generics.__func__
        return staticmethod(sm)
    elif isinstance(generics, classmethod):
        def cm(*args, **kwargs):
            raise Exception('classmethod has been exported.')
        cm.__export__ = generics.__func__
        return classmethod(cm)
    elif inspect.isfunction(generics):
        generics = _except('__except__')(generics)
        generics.__export__ = generics
        return generics


# 复原
def deport(cls, dep=1):
    if dep != 0:
        if inspect.isclass(cls):
            if inspect.getmodule(cls) is inspect.getmodule(deport):
                if hasattr(cls, '__cls__'):
                    return deport(getattr(cls, '__cls__'), dep=dep - 1)
    return cls
