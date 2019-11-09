#!/usr/local/bin/python3
import json
import base64
import asyncio
from .gdbcli import GdbController, GdbError
SESSIONS = {}


def onopen(token, emit):
    if token not in SESSIONS:
        session = Session(token)
        session.onlock = asyncio.Lock()
        SESSIONS[token] = session
    emit.onopen = asyncio.ensure_future(_onopen(token, emit))
    emit.onmessages = []


async def _onopen(token, emit):
    session = SESSIONS[token]
    async with session.onlock:
        await session.onopen(emit)
    emit.onopen = None


def onmessage(token, emit, data):
    assert isinstance(data, dict)
    emit.onmessages.append(asyncio.ensure_future(_onmessage(token, emit, data)))


async def _onmessage(token, emit, data):
    session = SESSIONS[token]
    if emit.onopen:
        await emit.onopen
    await session.onmessage(emit, data)
    emit.onmessages.remove(asyncio.Task.current_task())


def onclose(token, emit):
    asyncio.ensure_future(_onclose(token, emit))


async def _onclose(token, emit):
    session = SESSIONS[token]
    if emit.onopen:
        await emit.onopen
    while emit.onmessages:
        await emit.onmessages[0]
    async with session.onlock:
        await session.onclose(emit)


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

    async def onopen(self, emit):
        if not self._emits:
            try:
                self._ctrl = await WsGdbController.anew(json.loads(self._token))
            except BaseException as e:
                print(repr(e))
        self._emits.append(emit)
        if self._ctrl:
            for key in WsGdbController.PUSH:
                val = getattr(self._ctrl, key)
                self.notify(key, val, emit=emit)
        else:
            self.notify('ctrl', None, emit=emit)

    async def onmessage(self, emit, data):
        if data.get('type') == 'pull':
            method = data.get('method')
            params = data.get('params', ())
            tag = data.get('tag')
            try:
                assert method in WsGdbController.PULL, 'no method'
                r = await getattr(self._ctrl, method)(*params)
                if tag is not None:
                    emit({'type': 'pull', 'tag': tag, 'r': suit_js(r), 'e': None, })
            except BaseException as e:
                if tag is not None:
                    emit({'type': 'pull', 'tag': tag, 'r': None, 'e': suit_js(e), })

    async def onclose(self, emit):
        self._emits.remove(emit)
        if not self._emits:
            if self._ctrl:
                try:
                    await self._ctrl.adel()
                except BaseException as e:
                    print(repr(e))
                self._ctrl = None

    def notify(self, key, val, emit=None):
        if emit is None:
            for emit in self._emits:
                self.notify(key, val, emit=emit)
        else:
            emit({'type': 'push', 'key': key, 'val': suit_js(val), })


def push_prop(name, default):
    _name = '_' + name

    def fget(self):
        return getattr(self, _name, default)

    def notify(self):
        for session in SESSIONS.values():
            if session._ctrl is self:
                session.notify(name, fget(self))

    def fset(self, value):
        try:
            setattr(self, _name, value)
        finally:
            notify(self)

    def fdel(self):
        try:
            delattr(self, _name)
        finally:
            notify(self)
    return property(fget, fset, fdel)


class WsGdbController(GdbController):
    PULL = ('next', 'step', 'cont', 'ir', 'xb',)
    PUSH = ('suspend', 'breakpoints', 'watchpoints',)
    suspend = push_prop('suspend', False)
    breakpoints = push_prop('breakpoints', [])
    watchpoints = push_prop('watchpoints', [])

    async def next(self):
        self.suspend = False
        ret = await super().next()
        await asyncio.sleep(3)
        self.suspend = True
        return ret

    @classmethod
    async def anew(cls, config):
        self = await super().anew(config)
        self.suspend = True  # for test
        self.watchpoints.append({'address': 224})
        self.watchpoints = self.watchpoints
        return self
