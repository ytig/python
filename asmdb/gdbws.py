#!/usr/local/bin/python3
import base64
import asyncio
from .gdbcli import GdbController, GdbError
SESSIONS = {}


def onopen(token, emit):
    if token not in SESSIONS:
        session = Session(token)
        session._transfer = (asyncio.Lock(), [],)
        SESSIONS[token] = session
    session = SESSIONS[token]
    session._transfer[1].append(session.onopen(emit))
    asyncio.ensure_future(_transfer(*session._transfer))


def onmessage(token, emit, data):
    session = SESSIONS[token]
    session._transfer[1].append(session.onmessage(emit, data))
    asyncio.ensure_future(_transfer(*session._transfer))


def onclose(token, emit):
    session = SESSIONS[token]
    session._transfer[1].append(session.onclose(emit))
    asyncio.ensure_future(_transfer(*session._transfer))


async def _transfer(lock, coros):  # todo optimize lock
    async with lock:
        while coros:
            await coros.pop(0)


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
            self._ctrl = await WsGdbController.anew(self._token)
        self._emits.append(emit)
        # todo send push

    async def onmessage(self, emit, data):
        if data.get('type') == 'pull':
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

    async def onclose(self, emit):
        self._emits.remove(emit)
        if not self._emits:
            await self._ctrl.adel()
            self._ctrl = None


class WsGdbController(GdbController):
    PULL = ('next', 'step', 'cont', 'xb',)
    PUSH = ('suspend',)

    @property
    def suspend(self):
        return False

    @suspend.setter
    def suspend(self, value):
        pass
