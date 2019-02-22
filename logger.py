#!/usr/local/bin/python3
import sys
from decorator import clock


class Printer:
    # 打印
    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    # 着色
    def paint(self, *args, **kwargs):
        file = kwargs.get('file')
        if file is None:
            file = sys.stdout
        if file.isatty():
            print(*args, **kwargs)


class Log:
    VERBOSE = 2  # 冗长
    DEBUG = 3  # 调试
    INFO = 4  # 信息
    WARN = 5  # 警告
    ERROR = 6  # 异常
    ASSERT = 7  # 断言
    LEVEL = INFO  # 日志级别
    LOGGER = Printer()  # 日志输出

    # 打印日志
    @staticmethod
    @clock(lambda: __class__)
    def log(level, *args, tag=None):
        if level < Log.LEVEL:
            return False
        color = {Log.WARN: 34, Log.ERROR: 31, }.get(level)
        if color is not None:
            Log.LOGGER.paint('\033[0;%d;48m' % (color,), end='', flush=True)
        if tag is not None:
            args = ({Log.VERBOSE: 'V', Log.DEBUG: 'D', Log.INFO: 'I', Log.WARN: 'W', Log.ERROR: 'E', Log.ASSERT: 'A', }.get(level) + '/' + tag + ':', *args,)
        Log.LOGGER.print(*args, flush=True)
        if color is not None:
            Log.LOGGER.paint('\033[0m', end='', flush=True)
        return True

    @staticmethod
    def v(*args, **kwargs):
        return Log.log(Log.VERBOSE, *args, **kwargs)

    @staticmethod
    def d(*args, **kwargs):
        return Log.log(Log.DEBUG, *args, **kwargs)

    @staticmethod
    def i(*args, **kwargs):
        return Log.log(Log.INFO, *args, **kwargs)

    @staticmethod
    def w(*args, **kwargs):
        return Log.log(Log.WARN, *args, **kwargs)

    @staticmethod
    def e(*args, **kwargs):
        return Log.log(Log.ERROR, *args, **kwargs)

    @staticmethod
    def a(*args, **kwargs):
        return Log.log(Log.ASSERT, *args, **kwargs)
