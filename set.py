#!/usr/local/bin/python3
import inspect
from kit import trace
from decorator import Lock
from task import Tree
from log import Log


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


# 异常
def error(obj, e):
    Log.e(e, tag=getattr(trace(), '__name__', ''))


# 导出
def export(generics):
    """
    generics must be class, staticmethod, classmethod, function.
    class: export Set class, the original class is Set.__cls__.
    staticmethod, classmethod: export Set class constructor.
    function: export Set class forin method.

    Set.setting and Set.getting are used to define configure.
    e: exception handler, default @error.
    t: thread count, default 0.
    """
    if inspect.isclass(generics):
        def decorator(function):
            def wrapper(self, *args, **kwargs):
                objects = getattr(self, '_Set__objects')
                setting = self.getting()

                def call(obj):
                    try:
                        return function(obj, *args, **kwargs)
                    except BaseException as e:
                        try:
                            with Lock(self):
                                objects.remove(obj)
                            setting['e'](obj, e)
                        except BaseException:
                            pass
                        raise
                return _exec(call, *objects, t=setting['t'])
            return wrapper

        def imports(l):
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
                    'e': lambda e: e if callable(e) else error,
                    't': lambda t: t if isinstance(t, int) and t >= 0 else 0,
                }
                self.setting(**setting)

            def __len__(self):
                return len(self.__objects)

            # 写设置
            def setting(self, **setting):
                self.__setting.update(setting)
                return self

            # 读设置
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
        generics.__export__ = generics
        return generics


# 复原
def deport(cls, dep=1):
    if dep != 0 and hasattr(cls, '__cls__'):
        return deport(getattr(cls, '__cls__'), dep=dep - 1)
    else:
        return cls
