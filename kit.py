#!/usr/local/bin/python3
import re
import gc
import os
import sys
import types
import inspect
import threading
import traceback
import itertools
_LOCK = threading.RLock()  # 全局锁
CWDS = []  # 历史目录
WORKSPACE = None  # 工作区目录
COUNT = itertools.count(1)  # 无限递增迭代


# 标准输入
def input(prompt=None):
    if prompt is not None:
        print(prompt, end='', flush=True)
    with os.popen('read -e input;echo ${input};') as f:
        return f.read().rstrip('\n')


# 切换目录
def chdir(path):
    with _LOCK:
        dirname = os.getcwd()
        ret = os.chdir(path)
        CWDS.append(dirname)
    return ret


# 工作区目录
def workspace():
    with _LOCK:
        global WORKSPACE
        if WORKSPACE is None:
            if sys.argv and sys.argv[0]:
                if CWDS and not os.path.isabs(sys.argv[0]):
                    WORKSPACE = os.path.dirname(os.path.realpath(os.path.join(CWDS[0], sys.argv[0])))
                else:
                    WORKSPACE = os.path.dirname(os.path.realpath(sys.argv[0]))
            else:
                if CWDS:
                    WORKSPACE = CWDS[0]
                else:
                    WORKSPACE = os.getcwd()
        return WORKSPACE


# 守护进程
def daemon(dirname=None, stdin=None, stdout=None, stderr=None):
    def touch(dirname, file):
        if not os.path.isabs(file):
            file = os.path.join(dirname, file)
        dirname = os.path.dirname(file)
        if not os.path.exists(file):
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            open(file, mode='w').close()
        return file
    if dirname is None:
        dirname = workspace() + '/.daemon/' + (os.path.basename(sys.argv[0]).split('.', 1)[0] if sys.argv and sys.argv[0] else '') + '.std'
    if stdin is None:
        stdin = '0'
    if stdout is None:
        stdout = '1'
    if stderr is None:
        stderr = '2'
    if os.fork() != 0:
        exit()
    chdir('/')
    os.setsid()
    os.umask(0)
    if os.fork() != 0:
        exit()
    e = open(touch(dirname, stderr), mode='a', buffering=1)
    os.dup2(e.fileno(), sys.__stderr__.fileno())
    sys.stderr = e
    o = open(touch(dirname, stdout), mode='a', buffering=1)
    os.dup2(o.fileno(), sys.__stdout__.fileno())
    sys.stdout = o
    i = open(touch(dirname, stdin), mode='r')
    os.dup2(i.fileno(), sys.__stdin__.fileno())
    sys.stdin = i


def _inject(segm, argv):
    def decorator(function):
        def wrapper():
            args = []
            if argv:
                if segm is None:
                    for arg in argv:
                        if not args:
                            args.append(arg)
                        else:
                            if arg.startswith('-'):
                                break
                            else:
                                args.append(arg)
                elif segm:
                    for arg in argv[1:]:
                        if not args:
                            if arg == '-':
                                break
                            elif arg == '-' + segm:
                                args.append(arg)
                        else:
                            if arg.startswith('-'):
                                break
                            else:
                                args.append(arg)
                else:
                    a = argv[1:]
                    if '-' in a:
                        args = a[a.index('-'):]
            fullargspec = inspect.getfullargspec(function)
            d = len(args) - len(fullargspec.args)
            if d < 0:
                return function(*args + [None for i in range(-d)])
            elif d == 0 or fullargspec.varargs is not None:
                return function(*args)
            else:
                return function(*args[:-d])
        return wrapper
    return decorator


# 注入参数（装饰器）
def injects(*segms, argv=sys.argv):
    def parse(generics):
        if isinstance(generics, str):
            kv = generics.split('#')
            k = {'^': None, '$': '', }.get(kv[0], kv[0])
            v = int(kv[1]) if 1 < len(kv) and kv[1] else -1
        else:
            kv = generics
            k = kv[0]
            v = kv[1] if 1 < len(kv) else -1
        return (k, v,)
    segms = [parse(g) for g in segms]

    def decorator(function):
        def wrapper():
            args = []
            for segm, argc, in segms:
                _argv = _inject(segm, argv)(lambda *args: args)()
                if argc == 0:
                    args.append(len(_argv) > 0)
                elif argc > 0:
                    for i in range(argc):
                        args.append(_argv[i + 1] if i < len(_argv) - 1 else None)
                else:
                    args.append(_argv[1:])
            return function(*args)
        return wrapper
    return decorator


# 唯一编号
def unique():
    with _LOCK:
        return str(next(COUNT))


# 搜索
class search:
    def __init__(self, find):
        self.find = find

    # 深度优先
    def depth(self, *nodes):
        for node in nodes:
            yield node
            child = self.find(node)
            if child:
                yield from search.depth(self, *child)

    # 广度优先
    def breadth(self, *nodes):
        children = []
        for node in nodes:
            yield node
            child = self.find(node)
            if child:
                children.extend(child)
        if children:
            yield from search.breadth(self, *children)


# 检查变量
def hasvar(o, k):
    return hasattr(o, '__dict__') and isinstance(o.__dict__, (dict, types.MappingProxyType,)) and k in o.__dict__


# 获取变量
def getvar(o, k, d=None):
    return o.__dict__.get(k, d) if hasattr(o, '__dict__') and isinstance(o.__dict__, (dict, types.MappingProxyType,)) else d


# 设置变量
def setvar(o, k, v):
    if hasattr(o, '__dict__'):
        if isinstance(o.__dict__, dict):
            o.__dict__[k] = v
            return True
        elif isinstance(o.__dict__, types.MappingProxyType):
            b = True
            for c in type.mro(type(o)):
                if hasvar(c, k):
                    tp = type(getvar(c, k))
                    if hasattr(tp, '__set__') or hasattr(tp, '__delete__'):
                        b = False
                    break
            if b:
                try:
                    setattr(o, k, v)
                except TypeError:
                    b = False
            return b
    return False


# 检查定义
def appliable(o, k):
    for c in type.mro(type(o)):
        if hasvar(c, k):
            return True
    return False


def _apply(var, bug={
    object.__dict__['__new__']: 0,
    object.__dict__['__init_subclass__']: 1,
    object.__dict__['__subclasshook__']: 1,
}):
    if var in bug:
        val = bug[var]
        if isinstance(val, int):
            val = (var, val,)
        return val
    elif isinstance(var, staticmethod):
        return (var.__func__, 0,)
    elif isinstance(var, classmethod):
        return (var.__func__, 1,)
    elif callable(var):
        return (var, 2,)
    else:
        return (var, -1,)


# 运用定义
def apply(*args, **kwargs):
    assert len(args) > 1
    o = args[0]
    k = args[1]
    args = args[2:]
    for c in type.mro(type(o)):
        if hasvar(c, k):
            call, mode, = _apply(getvar(c, k))
            if mode == 0:
                return call(*args, **kwargs)
            elif mode == 1:
                return call(type(o), *args, **kwargs)
            elif mode == 2:
                return call(o, *args, **kwargs)
            raise TypeError
    raise NotImplementedError


# 执行函数
def call(*args, **kwargs):
    assert len(args) > 0
    func = args[0]
    args = args[1:]
    return func(*args, **kwargs)


# 获取闭包
def getnonlocals(func, name):
    return dict(zip(func.__code__.co_freevars, func.__closure__))[name].cell_contents


# 栈帧
class frames(list):
    # 追溯模式
    @staticmethod
    def traceback(e=None):
        def make():
            if e is None:
                ret = inspect.trace()
            else:
                ret = inspect.getinnerframes(e.__traceback__)
            ret.reverse()
            return ret
        return make

    def __init__(self, back=0, keep=None, make=None):
        super().__init__([i.frame for i in (make() if make else inspect.stack()[1:])[back:] if not keep or keep(i.frame)])

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.clear()

    # 检查索引
    def has(self, index=0):
        length = len(self)
        return index >= -length and index < length

    # 迭代深度
    def depth(self, index=0, equal=None):
        assert self.has(index=index)
        ret = 0
        back = self[index].f_back
        while back:
            if back.f_code is self[index].f_code and (not equal or equal(self[index], back)):
                ret += 1
            back = back.f_back
        return ret

    # 模块检索
    def module(self, index=0):
        assert self.has(index=index)
        for m in sys.modules.copy().values():
            if vars(m) is self[index].f_globals:
                return m
        return None

    # 作用域值
    def scope(self, index=0, pattern=None):
        assert self.has(index=index)
        ret = dict()
        try:
            keys = set()
            if isinstance(pattern, str):
                b = False
                for owner in gc.get_referrers(self[index].f_code):
                    if not inspect.isfunction(owner):
                        continue
                    if getattr(owner, '__globals__', None) is not self[index].f_globals:
                        continue
                    if re.search(pattern, getattr(owner, '__qualname__', '')) is None:
                        continue
                    b = True
                    ret['args'] = list()
                    ret['kwargs'] = dict()
                    fullargspec = inspect.getfullargspec(owner)
                    for key in fullargspec.args:
                        ret['args'].append(self[index].f_locals.get(key))
                        keys.add(key)
                    if fullargspec.varargs is not None:
                        ret['args'].extend(self[index].f_locals.get(fullargspec.varargs) or [])
                        keys.add(fullargspec.varargs)
                    for key in fullargspec.kwonlyargs:
                        ret['kwargs'][key] = self[index].f_locals.get(key)
                        keys.add(key)
                    if fullargspec.varkw is not None:
                        ret['kwargs'].update(self[index].f_locals.get(fullargspec.varkw) or {})
                        keys.add(fullargspec.varkw)
                    ret['args'] = tuple(ret['args'])
                    break
                assert b
            ret['varnames'] = dict()
            ret['cellvars'] = dict()
            ret['freevars'] = dict()
            for key in self[index].f_code.co_varnames:
                if key in keys:
                    continue
                if key in self[index].f_locals:
                    ret['varnames'][key] = self[index].f_locals[key]
            for key in self[index].f_code.co_cellvars:
                if key in keys:
                    continue
                if key in self[index].f_locals:
                    ret['cellvars'][key] = self[index].f_locals[key]
            for key in self[index].f_code.co_freevars:
                if key in keys:
                    continue
                if key in self[index].f_locals:
                    ret['freevars'][key] = self[index].f_locals[key]
        finally:
            owner = None
        return ret
