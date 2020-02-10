#!/usr/local/bin/python3
import json
import urllib
import base64
import signal
import asyncio
import tempfile
import traceback
import ptyprocess
from .backend import GdbController, GdbError, binary_search
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


def parse_token(token):
    return json.loads(urllib.parse.unquote(token))


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
                self._ctrl = await WsGdbController.anew(self._token, lambda msg: self.notify('anew', msg + '\n', emit=emit))
            except BaseException as e:
                traceback.print_exc()
        self._emits.append(emit)
        if self._ctrl:
            self.notify('ctrl', True, emit=emit)
            for key in WsGdbController.PUSH:
                val = getattr(self._ctrl, key)
                self.notify(key, val, emit=emit)
        else:
            self.notify('ctrl', False, emit=emit)

    async def onmessage(self, emit, data):
        if emit not in self._emits:
            return
        if data.get('type') == 'pull':
            method = data.get('method')
            params = data.get('params', ())
            xid = data.get('xid')
            try:
                assert method in WsGdbController.PULL, 'no method'
                r = await getattr(self._ctrl, method)(*params)
                if xid is not None:
                    emit({'type': 'pull', 'xid': xid, 'r': suit_js(r), 'e': None, })
            except BaseException as e:
                traceback.print_exc()
                if xid is not None:
                    emit({'type': 'pull', 'xid': xid, 'r': None, 'e': suit_js(e), })

    async def onclose(self, emit):
        if emit not in self._emits:
            return
        self._emits.remove(emit)
        if not list(filter(lambda i: not i.daemon, self._emits)):
            self.notify('exit', None)
            self._emits.clear()
            if self._ctrl:
                try:
                    await self._ctrl.adel()
                except BaseException as e:
                    traceback.print_exc()
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


class Terminal(asyncio.Protocol):
    @classmethod
    async def anew(cls, argv, notify_len, exit):
        self = cls()
        self.logfile = tempfile.NamedTemporaryFile()
        self.process = ptyprocess.PtyProcess.spawn(argv)
        self.notify_len = notify_len
        self.exit = exit
        await asyncio.get_event_loop().connect_read_pipe(self, self.process)
        return self

    async def adel(self):
        if not self.process.fileobj.closed:
            if self.exit:
                self.process.sendcontrol('c')
                self.process.write(self.exit)
            else:
                self.process.kill(signal.SIGKILL)
        self.logfile.close()

    def data_received(self, data):
        if self.logfile.closed:
            return
        self.logfile.seek(0, 2)
        self.logfile.write(data)
        self.notify_len(len(self))

    async def setwinsize(self, rows, cols):
        if self.process.isalive():
            self.process.setwinsize(rows, cols)

    async def readb(self, offset):
        if self.logfile.closed:
            raise IOError('read of closed file')
        self.logfile.seek(offset)
        return self.logfile.read()

    async def writeb(self, b):
        if self.process.fileobj.closed:
            raise IOError('write to closed file')
        self.process.write(b)

    def __len__(self):
        return self.logfile.seek(0, 2)

    def __call__(self):
        return self


class WsGdbController(GdbController):
    PULL = ('next', 'step', 'cont', 'rlse', 'asm', 'reg', 'mem', 'bpt', 'wpt', 'asgn', 'setwinsize', 'readb', 'writeb', 'ex',)
    PUSH = ('quit', 'suspend', 'breakpoints', 'watchpoints', 'maps', 'lenb',)
    quit = push_prop('quit', False)
    suspend = push_prop('suspend', False)
    breakpoints = push_prop('breakpoints', None)
    watchpoints = push_prop('watchpoints', None)
    maps = push_prop('maps', None)
    lenb = push_prop('lenb', 0)

    @classmethod
    async def anew(cls, token, println):
        config = parse_token(token)
        self = await super().anew(config, println)
        try:
            self.quit = False
            self.suspend = True
            self.breakpoints = []
            self.watchpoints = []
            self.maps = await self._info_maps()
            argv = ['python3', ]
            argv.append('-q')
            script = config.get('script')
            if script:
                argv.append('-i')
                argv.append(script)
                argv.append(token)
            else:
                argv.append('-')
                argv.append(token)
            self.terminal = await Terminal.anew(argv, lambda lenb: setattr(self, 'lenb', lenb), b'exit()\n')
            try:
                self.lenb = 0
                asyncio.ensure_future(self._beat(1))
            except BaseException:
                await self.terminal.adel()
                raise
            return self
        except BaseException:
            await super(__class__, self).adel()
            raise

    async def adel(self):
        try:
            self.quit = True
        finally:
            try:
                await self.terminal.adel()
            finally:
                await super().adel()

    async def _beat(self, interval):
        while not self.quit:
            if not await self._is_alive():
                self.quit = True
            else:
                await asyncio.sleep(interval)

    async def ex(self, command):
        return await self._command(command)

    async def setwinsize(self, rows, cols):
        return await self.terminal.setwinsize(rows, cols)

    async def readb(self, offset):
        return await self.terminal.readb(offset)

    async def writeb(self, b64):
        b = base64.b64decode(b64)
        return await self.terminal.writeb(b)

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
            return False
        self.suspend = False
        await self._nexti()
        self.suspend = True
        return True

    async def step(self):
        if not self.suspend:
            return False
        self.suspend = False
        await self._stepi()
        self.suspend = True
        return True

    async def cont(self):
        if not self.suspend:
            return False
        self.suspend = False
        await self._continue()
        self.suspend = True
        return True

    async def rlse(self):
        if not self.suspend:
            return False
        # todo
        return True

    async def asm(self, start, end):  # todo
        import capstone
        mem = await self.mem(start, end)
        ret = []
        for i in capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB).disasm(mem, start):
            ret.append({
                'type': 'instruction',
                'address': i.address,
                'size': i.size,
                'mnemonic': i.mnemonic,
                'op_str': i.op_str,
            })
        return ret

    async def reg(self):
        return await self._info_registers()

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
        throw = 0
        breakpoints = {}
        for point in self.breakpoints:
            breakpoints[point['address']] = point
        for point in del_points:
            p = breakpoints.get(point['address'])
            if p is None:
                throw += 1
                continue
            if not p['disable']:
                await self.sub_bpt(p['address'])
            del breakpoints[p['address']]
        for point in set_points:
            p = {
                'address': await self.add_bpt(point['address']),
                'disable': point.get('disable') or False,
                'comment': point.get('comment') or ''
            }
            if p['address'] is None:
                throw += 1
                continue
            if p['disable']:
                await self.sub_bpt(p['address'])
            breakpoints[p['address']] = p
        self.breakpoints.clear()
        for address in sorted(breakpoints.keys()):
            self.breakpoints.append(breakpoints[address])
        self.breakpoints = self.breakpoints
        return throw

    async def add_bpt(self, address):
        if address < 0 or address >= 256**self._unit:
            return
        # todo adjust address
        points = await self._info_breakpoints()
        for point in points:
            if point['type'] != 'breakpoint':
                continue
            if point['address'] == address:
                return address
        await self._break(address)
        return address

    async def sub_bpt(self, address):
        points = await self._info_breakpoints()
        for point in points:
            if point['type'] != 'breakpoint':
                continue
            if point['address'] == address:
                await self._delete_breakpoints(point['num'])

    async def wpt(self, del_points, set_points):
        throw = 0
        watchpoints = {}
        for point in self.watchpoints:
            watchpoints[point['address']] = point
        for point in del_points:
            p = watchpoints.get(point['address'])
            if p is None:
                throw += 1
                continue
            await self.sub_wpt(p['address'])
            del watchpoints[p['address']]
        for point in set_points:
            p = {
                'address': await self.add_wpt(point['address']),
            }
            if p['address'] is None:
                throw += 1
                continue
            watchpoints[p['address']] = p
        self.watchpoints.clear()
        for address in sorted(watchpoints.keys()):
            self.watchpoints.append(watchpoints[address])
        self.watchpoints = self.watchpoints
        return throw

    async def add_wpt(self, address):
        if address < 0 or address >= 256**self._unit:
            return
        address -= address % self._unit
        if not self.maps_at(address, address + self._unit):
            return
        wnum = 0
        points = await self._info_breakpoints()
        for point in points:
            if point['type'] != 'watchpoint':
                continue
            if point['address'] == address:
                return address
            wnum += 1
        if wnum >= self._wlen:
            return
        await self._watch(address)
        return address

    async def sub_wpt(self, address):
        points = await self._info_breakpoints()
        for point in points:
            if point['type'] != 'watchpoint':
                continue
            if point['address'] == address:
                await self._delete_breakpoints(point['num'])

    async def asgn(self, express):
        if express.startswith('$'):
            await self._set(express)
        elif express.startswith('*'):
            await self._set('*(unsigned char*)' + express[1:])
        else:
            return
        notify_all(self, 'assigned', express)
