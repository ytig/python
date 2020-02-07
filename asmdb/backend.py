#!/usr/local/bin/python3
import os
import re
import socket
import signal
import asyncio
import tempfile
from asyncio.subprocess import PIPE, STDOUT, DEVNULL


def list_subprocess(pid):
    sub_pids = []
    for line in os.popen(f'ps -l|grep {pid}').read().strip().split('\n'):
        words = line.split()
        if int(words[2]) == pid:
            sub_pids.append(int(words[1]))
    return sub_pids


def kill_them(pid, sig):
    os.kill(pid, sig)
    for sub_pid in list_subprocess(pid):
        kill_them(sub_pid, sig)


class Device:
    @classmethod
    def from_string(cls, string):
        try:
            scheme, string, = string.split('://', 1)
            serial, kernel, = string.rsplit('#', 1)
        except BaseException:
            return None
        else:
            return cls(scheme, serial, kernel)

    def __init__(self, scheme, serial, kernel):
        self.scheme = scheme
        self.serial = serial
        self.kernel = kernel

    def __str__(self):
        return f'{self.scheme}://{self.serial}#{self.kernel}'


def dest_pair(address):
    try:
        host, port, = address.split(':')
        return (host, int(port),)
    except BaseException:
        raise TypeError


async def adb_shell(serial, cmd, su=False, daemon=False):
    if not su:
        command = f'adb -s {serial} shell {cmd}'
    else:
        command = f'adb -s {serial} shell "su -c \'{cmd}\'"'
    if not daemon:
        proc = await asyncio.create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)
        async for line in proc.stderr:
            assert not re.search(r'error: device .* not found', line.decode()), 'device not found'
        return (await proc.stdout.read()).decode()
    else:
        return await asyncio.create_subprocess_shell(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)


async def adb_startup(serial, process):
    pid = None
    pids_need_kill = []
    for line in (await adb_shell(serial, 'ps')).split('\n'):
        line = line.strip()
        if line.endswith(process):
            pid = line.split()[1]
        elif re.search(r'/data/.+server', line):
            pids_need_kill.append(line.split()[1])
    assert pid, 'process not found'
    if 'Permissive' not in (await adb_shell(serial, 'getenforce')):
        await adb_shell(serial, 'setenforce 0', su=True)
    for p in pids_need_kill:
        await adb_shell(serial, f'kill {p}', su=True)
    await adb_shell(serial, f'/data/gdbserver :29714 --attach {pid}', su=True, daemon=True)
    cmd = f'adb -s {serial} forward tcp:29714 tcp:29714'
    await (await asyncio.create_subprocess_shell(cmd, stdout=PIPE)).stdout.read()
    return '0.0.0.0:29714'


async def gdb_startup(config, println):
    device = config.get('device')
    process = config.get('process')
    assert device, 'no device selected'
    assert process, 'no process selected'
    d = Device.from_string(device)
    assert d and d.scheme in ('adb',) and d.kernel in ('arm32',), 'unkown device submitted'
    remote = None
    if d.scheme == 'adb':
        remote = await adb_startup(d.serial, process)
    commands = []
    commands.append('set confirm off')
    commands.append('set pagination off')
    if remote:
        commands.append(f'target remote {remote}')
    args = []
    args.append('--nx')
    args.append('-q')
    for cmd in commands:
        args.append('-ex')
        args.append(cmd)
    proc = await asyncio.create_subprocess_exec('gdb', *args, stdin=PIPE, stdout=PIPE, stderr=STDOUT, limit=2**20)
    buffer = b''
    while not buffer.endswith(b'(gdb) '):
        b = await proc.stdout.read(n=1)
        assert b, 'Remote connection closed'
        buffer += b
        lines = buffer.split(b'\n')
        for line in lines[:-1]:
            line = line.strip().decode()
            if line:
                println(line)
        buffer = lines[-1]
    proc.kernel = d.kernel
    if remote:
        _socket = socket.create_connection(dest_pair(remote))

        async def is_remote_alive():
            try:
                return bool(_socket.recv(1024, socket.MSG_DONTWAIT))
            except BlockingIOError:
                return True
            except ConnectionError:
                return False
        proc.is_remote_alive = is_remote_alive

        async def atexit():
            _socket.close()
        proc.atexit = atexit
    return proc


async def gdb_readlines(stream):
    separator = b'(gdb) '
    return (await stream.readuntil(separator=separator))[:-len(separator)]


class GdbError(RuntimeError):
    pass


def binary_search(a, x):
    lo = 0
    hi = len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        delta = x(a[mid])
        if delta == 0:
            return mid
        if delta > 0:
            lo = mid + 1
        else:
            hi = mid - 1
    return -(lo + 1)


class GdbController:
    @classmethod
    async def anew(cls, config, println):
        self = cls()
        try:
            self.process = await gdb_startup(config, println)
        except BaseException as e:
            println(str(e))
            raise
        self.cmdlock = asyncio.Lock()
        self.onelock = asyncio.Lock()
        self.twolock = asyncio.Lock()
        return self

    async def adel(self):
        if hasattr(self.process, 'atexit'):
            await self.process.atexit()
        kill_them(self.process.pid, signal.SIGINT)
        self.process.stdin.write(b'quit\n')

    @property
    def _unit(self):
        if self.process.kernel == 'arm32':
            return 4

    @property
    def _wlen(self):
        if self.process.kernel == 'arm32':
            return 4

    @property
    def _bend(self):
        if self.process.kernel == 'arm32':
            return False

    async def __command(self, command):
        async with self.cmdlock:
            self.process.stdin.write(command.encode() + b'\n')
            return (await gdb_readlines(self.process.stdout)).decode()

    async def _command(self, command, wait=False):
        if not wait:
            async with self.onelock:
                if self.cmdlock.locked():
                    kill_them(self.process.pid, signal.SIGINT)
                return await self.__command(command)
        else:
            async with self.twolock:
                while True:
                    async with self.onelock:
                        pass
                    text = await self.__command(command)
                    if 'SIGINT' not in text:
                        return text

    async def _is_alive(self):
        return not hasattr(self.process, 'is_remote_alive') or (await self.process.is_remote_alive())

    async def _nexti(self):
        text = await self._command('nexti')
        if re.search(r'Remote connection closed|The program is not being run.', text):
            raise GdbError(text.strip())

    async def _stepi(self):
        # gdb bug: stepi not worked?
        text = await self._command('stepi')
        if re.search(r'Remote connection closed|The program is not being run.', text):
            raise GdbError(text.strip())

    async def _continue(self):
        # gdb bug: Cannot set arm force-mode based on address?
        await self._command('set arm force-mode thumb')
        try:
            text = await self._command('continue', wait=True)
            if re.search(r'Remote connection closed|The program is not being run.', text):
                raise GdbError(text.strip())
        finally:
            await self._command('set arm force-mode auto')

    async def _info_maps(self):
        maps = []
        base = {}
        text = await self._command('info proc mappings')
        if re.search(r'Remote connection closed|No current process: you must name one.', text):
            raise GdbError(text.strip())
        lines = text.strip().split('\n')
        while 'objfile' not in lines.pop(0):
            pass
        for line in lines:
            words = line.split(maxsplit=4)
            start_addr = int(words[0], 16)
            end_addr = int(words[1], 16)
            objfile = words[-1] if len(words) == 5 else ''
            if start_addr >= end_addr:
                continue
            maps.append({
                'start': start_addr,
                'end': end_addr,
                'offset': 0,
                'target': objfile,
                'section': '',
            })
            if objfile and objfile not in base:
                base[objfile] = start_addr
        text = await self._command('info target')
        proc_file = re.search(r'Symbols from "target:(.*)"\.', text).group(1)
        lines = text.strip().split('\n')
        while 'Entry point:' not in lines.pop(0):
            pass
        for line in lines:
            words = line.split(maxsplit=3)
            start = int(words[0], 16)
            end = int(words[2], 16)
            words = words[3][3:].split(' in target:', maxsplit=1)
            if len(words) == 1:
                section = words[0]
                target = proc_file
            else:
                section, target, = words
            if start >= end:
                continue
            lo = binary_search(maps, lambda i: -1 if start < i['start'] else (1 if start >= i['end'] else 0))
            if lo < 0:
                lo = -1 - lo
            hi = binary_search(maps, lambda i: -1 if (end - 1) < i['start'] else (1 if (end - 1) >= i['end'] else 0))
            if hi < 0:
                hi = -1 - hi
            else:
                hi += 1
            sliced = []
            for i in range(lo, hi):
                sliced.append(maps.pop(lo))
            if sliced and sliced[-1]['end'] > end:
                m = sliced[-1]
                maps.insert(lo, {
                    'start': end,
                    'end': m['end'],
                    'offset': 0,
                    'target': m['target'],
                    'section': m['section'],
                })
            maps.insert(lo, {
                'start': start,
                'end': end,
                'offset': start - base.get(target, start),
                'target': target,
                'section': section,
            })
            if sliced and start > sliced[0]['start']:
                m = sliced[0]
                maps.insert(lo, {
                    'start': m['start'],
                    'end': start,
                    'offset': 0,
                    'target': m['target'],
                    'section': m['section'],
                })
        return maps

    async def _info_registers(self):
        registers = {}
        text = await self._command('info registers')
        if re.search(r'Remote connection closed|The program has no registers now.', text):
            raise GdbError(text.strip())
        for line in text.strip().split('\n'):
            words = line.split()
            registers[words[0]] = int(words[1], 16)
        return registers

    async def _dump(self, start, end):
        temp = tempfile.NamedTemporaryFile()
        try:
            text = await self._command(f'dump binary memory {temp.name} {start} {end}')
            if re.search(r'Remote connection closed|Cannot access memory at address', text):
                raise GdbError(text.strip())
            temp.seek(0)
            return temp.read()
        finally:
            temp.close()

    async def _info_breakpoints(self):
        points = []
        text = await self._command('info breakpoints')
        if not re.search(r'No breakpoints or watchpoints.', text):
            for line in text.split('\n'):
                if 'keep' not in line:
                    continue
                if 'breakpoint' in line:
                    words = line.split()
                    points.append({
                        'num': int(words[0]),
                        'type': 'breakpoint',
                        'address': int(words[4], 16)
                    })
                elif 'hw watchpoint' in line:
                    words = line.split()
                    points.append({
                        'num': int(words[0]),
                        'type': 'watchpoint',
                        'address': int(words[5][1:], 16)
                    })
        return points

    async def _delete_breakpoints(self, num):
        text = await self._command(f'delete breakpoints {num}')
        if re.search(r'No breakpoint number', text):
            raise GdbError(text.strip())

    async def _break(self, address):
        text = await self._command(f'break *{hex(address)}')
        if re.search(r'Remote connection closed', text):
            raise GdbError(text.strip())

    async def _watch(self, address):
        text = await self._command(f'watch *{hex(address)}')
        if re.search(r'Remote connection closed', text):
            raise GdbError(text.strip())

    async def _set(self, express):
        text = await self._command(f'set {express}')
        if re.search(r'Remote connection closed|Cannot access memory at address', text):
            raise GdbError(text.strip())
