#!/usr/local/bin/python3
import sys


class WsController:
    def __init__(self, url, token):
        # todo
        pass


_ctrl = None


def ctrl():
    if _ctrl is None:
        _ctrl = WsController('ws://0.0.0.0:8519/ws', sys.argv[1])
    return _ctrl
