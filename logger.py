#!/usr/local/bin/python3
import sys
import logging


class BasicFormatter(logging.Formatter):
    def format(self, record):
        record.message = record.getMessage()
        if record.name is None:
            s = record.message
        else:
            if self.usesTime():
                record.asctime = self.formatTime(record, self.datefmt)
            s = self.formatMessage(record)
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s and s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s and s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s


class BasicHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(stream=sys.stdout)
        self.formatter = BasicFormatter(fmt='{levelname[0]}/{name}: {message}', style='{')

    def format(self, record):
        s = super().format(record)
        if self.stream.isatty():
            color = {30: 34, 40: 31, }.get(record.levelno)
            if color is not None:
                s = '\033[0;%d;48m%s\033[0m' % (color, s,)
        return s


# 配置
def config(level=logging.INFO):
    logging._acquireLock()
    try:
        if len(logging.root.handlers) == 0:
            logging.root.name = None
            logging.basicConfig(handlers=(BasicHandler(),), level=level)
            return True
        else:
            return False
    finally:
        logging._releaseLock()


# 调试
def debug(*args, tag=None):
    if len(logging.root.handlers) == 0:
        config()
    logging.getLogger(name=tag).debug(' '.join(str(arg) for arg in args))


# 信息
def info(*args, tag=None):
    if len(logging.root.handlers) == 0:
        config()
    logging.getLogger(name=tag).info(' '.join(str(arg) for arg in args))


# 警告
def warning(*args, tag=None):
    if len(logging.root.handlers) == 0:
        config()
    logging.getLogger(name=tag).warning(' '.join(str(arg) for arg in args))


# 错误
def error(*args, tag=None):
    if len(logging.root.handlers) == 0:
        config()
    logging.getLogger(name=tag).error(' '.join(str(arg) for arg in args))


d = debug
i = info
w = warning
e = error


# 异常
def exception(e):
    if len(logging.root.handlers) == 0:
        config()
    if e is None:
        logging.exception('')
    else:
        assert isinstance(e, BaseException)
        logging.exception('', exc_info=e)
