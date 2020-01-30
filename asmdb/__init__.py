#!/usr/local/bin/python3
import sys


class WsController:
    def __init__(self, host, port, token):
        # todo
        pass


_ctrl = None


def ctrl():
    if _ctrl is None:
        _ctrl = WsController('0.0.0.0', 8519, sys.argv[1])
    return _ctrl
