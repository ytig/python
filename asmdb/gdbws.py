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
    asyncio.ensure_future(SESSIONS[token].request(emit, data))


def onclose(token, emit):
    SESSIONS[token].logout(emit)


def suit_js(obj):
    if isinstance(obj, (tuple, list,)):
        return list(suit_js(i) for i in obj)
    if isinstance(obj, dict):
        return dict((k, suit_js(v),) for k, v, in obj.items())
    if isinstance(obj, (bytes, bytearray,)):
        return base64.b64encode(obj).decode()
    if isinstance(obj, BaseException):
        return str(obj)
    return obj


class Session:
    def __init__(self, token):
        self._token = token
        self._emits = []
        self._ctrl = None

    def login(self, emit):
        if not self._emits:
            self._new()
        self._emits.append(emit)

    async def request(self, emit, data):  # todo
        if data.get('type') == 'pull':
            method = data['method']
            params = data.get('params', ())
            tag = data.get('tag')
            try:
                r = await getattr(self._ctrl, method)(*params)
                if tag is not None:
                    emit({'type': 'pull', 'tag': tag, 'r': suit_js(r), 'e': None, })
            except BaseException as e:
                if tag is not None:
                    emit({'type': 'pull', 'tag': tag, 'r': None, 'e': suit_js(e), })

    def logout(self, emit):
        self._emits.remove(emit)
        if not self._emits:
            self._del()

    def _new(self):
        pass

    def _del(self):
        pass


class GdbController(GdbDebugger):
    pass
