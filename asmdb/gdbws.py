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
                print(repr(e))
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


def notify_all(ctrl, key, val):
    for session in SESSIONS.values():
        if session._ctrl is ctrl:
            session.notify(key, val)


def push_prop(name, default):
    _name = '_' + name

    def fget(self):
        return getattr(self, _name, default)

    def fset(self, value):
        try:
            setattr(self, _name, value)
        finally:
            notify_all(self, name, fget(self))

    def fdel(self):
        try:
            delattr(self, _name)
        finally:
            notify_all(self, name, fget(self))
    return property(fget, fset, fdel)


class WsGdbController(GdbController):
    PULL = ('next', 'step', 'cont', 'rlse', 'asm', 'reg', 'mem', 'bpt', 'wpt', 'asgn')
    PUSH = ('suspend', 'breakpoints', 'watchpoints',)
    suspend = push_prop('suspend', False)
    breakpoints = push_prop('breakpoints', None)
    watchpoints = push_prop('watchpoints', None)

    @classmethod
    async def anew(cls, config):
        self = await super().anew(config)
        self.suspend = True  # for test
        self.pc = 0x3210
        self.breakpoints = []
        self.watchpoints = []
        return self

    async def next(self):
        self.suspend = False
        await asyncio.sleep(0.05)
        self.suspend = True

    async def step(self):
        pass

    async def cont(self):
        pass

    async def rlse(self):
        pass

    async def asm(self, start, end):
        ret = []
        for address in range(start, end, 4):
            ret.append({
                'type': 'instruction',
                'address': address,
                'mnemonic': 'push',
                'op_str': 'r0 r1'
            })
        return ret

    async def reg(self):
        d = {}
        for k in ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr']:
            d[k] = 0
        self.pc += 4
        d['pc'] = self.pc
        return d

    async def mem(self, start, end):
        import random
        ret = b''
        for i in range(end - start):
            if random.random() < 0.01:
                ret += b'\x00'
            else:
                ret += b'\x66'
        return ret

    async def bpt(self, del_points, set_points):
        breakpoints = {}
        for point in self.breakpoints:
            breakpoints[point['address']] = point
        for point in del_points:
            if point['address'] in breakpoints:
                del breakpoints[point['address']]
        for point in set_points:
            breakpoints[point['address']] = point
        self.breakpoints.clear()
        for address in sorted(breakpoints.keys()):
            self.breakpoints.append(breakpoints[address])
        self.breakpoints = self.breakpoints

    async def wpt(self, del_points, set_points):
        watchpoints = {}
        for point in self.watchpoints:
            watchpoints[point['address']] = point
        for point in del_points:
            if point['address'] in watchpoints:
                del watchpoints[point['address']]
        for point in set_points:
            watchpoints[point['address']] = point
        self.watchpoints.clear()
        for address in sorted(watchpoints.keys()):
            self.watchpoints.append(watchpoints[address])
        self.watchpoints = self.watchpoints

    async def asgn(self, express):
        notify_all(self, 'assigned', express)
