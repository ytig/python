#!/usr/local/bin/python3
import base64
import asyncio
from .gdbmi import GdbDebugger, GdbError
SESSIONS = {}


def onopen(token, emit):
    if token not in SESSIONS:
        SESSIONS[token] = Session(token)
    SESSIONS[token].login(emit)


def onmessage(token, emit, data):
    SESSIONS[token].request(emit, data)


def onclose(token, emit):
    SESSIONS[token].logout(emit)


class Session:
    def __init__(self, token):
        self._token = token
        self._users = []

    def login(self, emit):
        if not self._users:
            self._new()
        self._users.append(emit)

    def request(self, emit, data):
        pass

    def logout(self, emit):
        self._users.remove(emit)
        if not self._users:
            self._del()

    def _new(self):
        pass

    def _del(self):
        pass


def suit_js(data):
    if isinstance(data, (bytes, bytearray,)):
        return base64.b64encode(data).decode()
    return data


class GdbController(GdbDebugger):
    pass
