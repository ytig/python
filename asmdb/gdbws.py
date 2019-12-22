#!/usr/local/bin/python3
import json
import base64
import threading
import asyncio
import ptyprocess
from .gdbcli import GdbController, GdbError, binary_search
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
    PULL = ('next', 'step', 'cont', 'rlse', 'asm', 'reg', 'mem', 'bpt', 'wpt', 'asgn', 'setwinsize', 'readb', 'writeb',)
    PUSH = ('quit', 'suspend', 'breakpoints', 'watchpoints', 'maps',)
    quit = push_prop('quit', False)
    suspend = push_prop('suspend', False)
    breakpoints = push_prop('breakpoints', None)
    watchpoints = push_prop('watchpoints', None)
    maps = push_prop('maps', None)

    @classmethod
    async def anew(cls, config):
        self = await super().anew(config)
        self.quit = False
        self.suspend = True  # for test
        self.breakpoints = []
        self.watchpoints = []
        # self.maps = await self._info_maps()
        self.maps = []
        self.terminal = ptyprocess.PtyProcess.spawn(['python3'])
        self._readb = b''

        def read_t():
            asyncio.set_event_loop(asyncio.new_event_loop())
            while True:
                try:
                    b = self.terminal.read()
                    self._readb += b
                    notify_all(self, 'readb', b)
                except EOFError:
                    break
        threading.Thread(target=read_t).start()
        return self

    async def adel(self):
        self.terminal.sendcontrol('c')
        self.terminal.write(b'exit()\n')
        await super().adel()

    def maps_at(self, start, end):
        lo = binary_search(self.maps, lambda i: -1 if start < i['start'] else (1 if start >= i['end'] else 0))
        if lo < 0:
            lo = -1 - lo
        hi = binary_search(self.maps, lambda i: -1 if (end - 1) < i['start'] else (1 if (end - 1) >= i['end'] else 0))
        if hi < 0:
            hi = -1 - hi
        else:
            hi += 1
        return self.maps[lo:hi]

    async def next(self):
        if not self.suspend:
            return
        self.suspend = False
        await self._nexti()
        self.suspend = True

    async def step(self):
        pass

    async def cont(self):
        if not self.suspend:
            return
        self.suspend = False
        await self._continue()
        self.suspend = True

    async def rlse(self):
        self.quit = True

    async def asm(self, start, end):  # todo
        mem = await self.mem(start, end)
        ret = []
        for i in range((end - start)):
            ret.append({
                'type': 'byte',
                'address': start + i,
                'size': 1,
                'value': mem[i],
            })
        return ret

    async def reg(self):
        # return await self._info_registers()
        return dict([(k, 1470,) for k in ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr']])

    async def mem(self, start, end):
        data = b''
        cursor = start
        for i in self.maps_at(start, end):
            if i['start'] > cursor:
                data += b'\x00' * (i['start'] - cursor)
                cursor = i['start']
            min_end = min(i['end'], end)
            if min_end > cursor:
                data += await self._dump(cursor, min_end)
                cursor = min_end
        if end > cursor:
            data += b'\x00' * (end - cursor)
            cursor = end
        return data

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

    async def setwinsize(self, rows, cols):
        self.terminal.setwinsize(rows, cols)

    async def writeb(self, b):
        self.terminal.write(b)

    async def readb(self):
        return self._readb
