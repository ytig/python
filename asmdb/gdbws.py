#!/usr/local/bin/python3
import base64
import asyncio
from .gdbcli import GdbController, GdbError
SESSIONS = {}


def onopen(token, emit):
    if token not in SESSIONS:
        SESSIONS[token] = Session(token)
    asyncio.ensure_future(SESSIONS[token].onopen(emit))


def onmessage(token, emit, data):
    asyncio.ensure_future(SESSIONS[token].onmessage(emit, data))


def onclose(token, emit):
    asyncio.ensure_future(SESSIONS[token].onclose(emit))


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


class RWLock:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.refs = 0

    async def acquire_read(self):
        if self.refs == 0:
            await self.lock.acquire()
        self.refs += 1

    def release_read(self):
        self.refs -= 1
        if self.refs == 0:
            self.lock.release()

    async def acquire_write(self):
        await self.lock.acquire()

    def release_write(self):
        self.lock.release()


class Session:
    def __init__(self, token):
        self._rwlock = RWLock()
        self._emits = []
        self._ctrl = None
        self._token = token

    async def onopen(self, emit):
        await self._rwlock.acquire_write()
        try:
            if not self._emits:
                self._ctrl = await WsGdbController.anew(self._token)
            self._emits.append(emit)
            # todo send push
        finally:
            self._rwlock.release_write()

    async def onmessage(self, emit, data):
        await self._rwlock.acquire_read()
        try:
            if data['type'] == 'pull':
                method = data['method']
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
        finally:
            self._rwlock.release_read()

    async def onclose(self, emit):
        await self._rwlock.acquire_write()
        try:
            self._emits.remove(emit)
            if not self._emits:
                await self._ctrl.adel()
                self._ctrl = None
        finally:
            self._rwlock.release_write()


class WsGdbController(GdbController):
    PULL = ('next', 'step', 'cont', 'xb',)
    PUSH = ('suspend',)

    @property
    def suspend(self):
        return False

    @suspend.setter
    def suspend(self, value):
        pass
