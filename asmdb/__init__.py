#!/usr/local/bin/python3
import sys
from .wsclient import WsController, WsError


def new_default_controller():
    return WsController('ws://0.0.0.0:8519/ws', sys.argv[1])
