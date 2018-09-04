#!/usr/local/bin/python3
import sys
import inspect
import pexpect


class spawn(pexpect.spawn):
    def __init__(self, *args, **kwargs):
        method = super().__init__
        ba = inspect.signature(method).bind(*args, **kwargs)
        if 'timeout' not in ba.arguments:
            ba.arguments['timeout'] = None
        if 'logfile' not in ba.arguments:
            logfile_read = sys.stdout.buffer
        else:
            logfile_read = ba.arguments['logfile']
            ba.arguments['logfile'] = None
        method(*ba.args, **ba.kwargs)
        self.logfile_read = logfile_read

    def interact(self, *args, **kwargs):
        self.logfile_read = None
        return super().interact(*args, **kwargs)
