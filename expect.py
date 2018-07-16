#!/usr/local/bin/python3
# coding:utf-8
from pexpect import *
import sys as _sys
_spawn = spawn


def spawn(*args, **kwargs):
    if 'logfile' not in kwargs:
        logfile = _sys.stdout.buffer
    else:
        logfile = kwargs['logfile']
        del kwargs['logfile']
    self = _spawn(*args, **kwargs)
    self.logfile_read = logfile
    _interact = self.interact

    def interact(*args, **kwargs):
        self.logfile_read = None
        return _interact(*args, **kwargs)
    self.interact = interact
    return self
