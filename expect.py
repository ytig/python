#!/usr/local/bin/python3
# coding:utf-8
from pexpect import *
import sys as _sys
_spawn = spawn


def spawn(*args, **kwargs):
    if 'logfile' not in kwargs:
        kwargs['logfile'] = _sys.stdout.buffer
    self = _spawn(*args, **kwargs)
    _logfile = self.logfile
    _expect = self.expect
    _interact = self.interact

    def expect(*args, **kwargs):
        self.logfile = _logfile
        ret = _expect(*args, **kwargs)
        self.logfile = None
        return ret

    def interact(*args, **kwargs):
        self.expect(['[\s\S]*'])
        return _interact(*args, **kwargs)
    self.interact = interact
    self.expect = expect
    self.logfile = None
    return self
