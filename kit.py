#!/usr/local/bin/python3
# coding:utf-8
import os
import sys
import inspect
import threading
_LOCK = threading.Lock()  # 目录锁
CWDS = []  # 历史目录
WORKSPACE = None  # 工作区目录
PASS = object()  # 跳过参数绑定


# 切换目录
def chdir(path):
    with _LOCK:
        dirname = os.getcwd()
        ret = os.chdir(path)
        CWDS.append(dirname)
        return ret


# 工作区目录
def workspace():
    global WORKSPACE
    if WORKSPACE is None:
        with _LOCK:
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
def daemon(dirname=None, stdin=None, stdout=None, stderr=None, g=vars(sys)):
    def touch(dirname, file):
        if os.path.isabs(file):
            dirname = os.path.dirname(file)
        else:
            file = os.path.join(dirname, file)
        if not os.path.exists(file):
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            open(file, 'w').close()
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
    stdin = open(touch(dirname, stdin), 'r')
    stdout = open(touch(dirname, stdout), 'a+')
    stderr = open(touch(dirname, stderr), 'a+')
    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())
    g['stdin2'] = stdin
    g['stdout2'] = stdout
    g['stderr2'] = stderr


# 绑定参数
def bind(*args, **kwargs):
    call = args[0] if len(args) else None
    if not callable(call):
        raise Exception('callable missing.')
    extends = args[1:]
    updates = kwargs

    def bound(*args, **kwargs):
        args = list(args)
        for i in range(len(extends)):
            arg = extends[i]
            if arg is PASS:
                if i >= len(args):
                    raise Exception('argument missing.')
            else:
                args.insert(i, arg)
        kwargs.update(updates)
        return call(*args, **kwargs)
    return bound


def _inject(segm=None, argv=sys.argv):
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
            spec = inspect.getfullargspec(function)
            d = len(args) - len(spec.args)
            if d < 0:
                return function(*args + [None for i in range(-d)])
            elif d == 0 or spec.varargs is not None:
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
        return k, v,
    segms = [parse(g) for g in segms]

    def decorator(function):
        def wrapper():
            args = []
            for segm, argc, in segms:
                @_inject(segm=segm, argv=argv)
                def f(*args):
                    return args
                _argv = f()
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


# 异常追溯
def trace():
    try:
        file = inspect.trace()[-1][1]
        for module in sys.modules.values():
            if getattr(module, '__file__', '') == file:
                return module
    except BaseException:
        pass
    return None
