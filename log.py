#!/usr/local/bin/python3
# coding:utf-8
import os
import datetime
from kit import workspace
from decorator import LOCK_CLASS, synchronized
from task import Queue


class Print(Queue):
    KEEP = False  # 持久化

    def __init__(self, *args, **kwargs):
        print(*args, **kwargs)
        if Print.KEEP and not kwargs:
            iso = datetime.datetime.now().isoformat()
            self.path = workspace() + '/.log/' + iso.split('T')[0]
            self.text = ' '.join([iso.split('T')[1]] + [str(i) for i in args])
            self.push()

    def pop(self):
        try:
            dirname = os.path.dirname(self.path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(self.path, mode='a') as f:
                f.write(self.text + '\n')
        except BaseException:
            pass


class Log:
    VERBOSE = 2  # 冗长
    DEBUG = 3  # 调试
    INFO = 4  # 信息
    WARN = 5  # 警告
    ERROR = 6  # 异常
    ASSERT = 7  # 断言
    LEVEL = INFO  # 日志级别
    PRINT = Print  # 日志打印

    @staticmethod
    def __tag(level, tag):
        return {Log.VERBOSE: 'V', Log.DEBUG: 'D', Log.INFO: 'I', Log.WARN: 'W', Log.ERROR: 'E', Log.ASSERT: 'A', }.get(level) + '/' + tag + ':'

    # 打印日志
    @staticmethod
    @synchronized(lock=LOCK_CLASS)
    def log(*args, tag=None, **kwargs):
        level = args[0]
        args = [args[i + 1] for i in range(len(args) - 1)]
        if level < Log.LEVEL:
            return False
        color = {Log.WARN: 34, Log.ERROR: 31, }.get(level)
        if color is not None:
            Log.PRINT('\033[0;%d;48m' % (color,), end='')
        if tag is not None:
            args.insert(0, Log.__tag(level, tag))
        Log.PRINT(*args)
        if color is not None:
            Log.PRINT('\033[0m', end='')
        return True

    @staticmethod
    def v(*args, **kwargs):
        return Log.log(*(Log.VERBOSE,) + args, **kwargs)

    @staticmethod
    def d(*args, **kwargs):
        return Log.log(*(Log.DEBUG,) + args, **kwargs)

    @staticmethod
    def i(*args, **kwargs):
        return Log.log(*(Log.INFO,) + args, **kwargs)

    @staticmethod
    def w(*args, **kwargs):
        return Log.log(*(Log.WARN,) + args, **kwargs)

    @staticmethod
    def e(*args, **kwargs):
        return Log.log(*(Log.ERROR,) + args, **kwargs)

    @staticmethod
    def a(*args, **kwargs):
        return Log.log(*(Log.ASSERT,) + args, **kwargs)
