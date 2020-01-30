#!/usr/local/bin/python3
import re
import tempfile
import signal
import asyncio
from asyncio import subprocess


async def adb_shell(serial, cmd, su=False, daemon=False):
    if not su:
        command = f'adb -s {serial} shell {cmd}'
    else:
        command = f'adb -s {serial} shell "su -c \'{cmd}\'"'
    if not daemon:
        proc = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        async for line in proc.stderr:
            assert not re.search(r'error: device .* not found', line.decode()), 'device not found'
        return (await proc.stdout.read()).decode()
    else:
        return await asyncio.create_subprocess_shell(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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
    await adb_shell(serial, f'/data/gdbserver :5039 --attach {pid}', su=True, daemon=True)
    cmd = f'adb -s {serial} forward tcp:5039 tcp:5039'
    await (await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE)).stdout.read()
    return '0.0.0.0:5039'


async def gdb_startup(config, println):
    device = config.get('device')
    process = config.get('process')
    assert device, 'no device selected'
    assert process, 'no process selected'
    remote = None
    scheme = serial = None
    if '://' in device:
        scheme, serial, = device.split('://', 1)
    if scheme == 'adb':
        remote = await adb_startup(serial, process)
    else:
        raise TypeError('unknown device type')
    exs = []
    exs.append('set pagination off')
    if remote:
        exs.append(f'target remote {remote}')
    args = []
    args.append('--nx')
    args.append('-q')
    for ex in exs:
        args.append('-ex')
        args.append(ex)
    proc = await asyncio.create_subprocess_exec('gdb', *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, limit=2**20)
    buffer = b''
    while not buffer.endswith(b'(gdb) '):
        buffer += await proc.stdout.read(n=1)
        lines = buffer.split(b'\n')
        for line in lines[:-1]:
            println(line.decode())
        buffer = lines[-1]
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
        self.process.send_signal(signal.SIGINT)
        self.process.stdin.write(b'quit\n')

    async def __command(self, command):
        async with self.cmdlock:
            self.process.stdin.write(command.encode() + b'\n')
            return (await gdb_readlines(self.process.stdout)).decode()

    async def _command(self, command, wait=False):
        if not wait:
            async with self.onelock:
                if self.cmdlock.locked():
                    self.process.send_signal(signal.SIGINT)
                return await self.__command(command)
        else:
            async with self.twolock:
                while True:
                    text = await self.__command(command)
                    if 'SIGINT' not in text:
                        return text

    async def _nexti(self):
        text = await self._command('nexti')
        if re.search(r'Remote connection closed|The program is not being run.', text):
            raise GdbError(text.strip())

    async def _continue(self):
        text = await self._command('continue', wait=True)
        if re.search(r'Remote connection closed|he program is not being run.', text):
            raise GdbError(text.strip())

    async def _info_maps(self):
        maps = []
        base = {}
        text = await self._command('info proc mappings')
        if re.search(r'Remote connection closed|No current process: you must name one.', text):
            raise GdbError(text.strip())
        for line in text.strip().split('\n'):
            if '0x' not in line:
                continue
            words = line.split(maxsplit=4)
            maps.append({
                'start': int(words[0], 16),
                'end': int(words[1], 16),
                'offset': 0,
                'target': words[-1] if len(words) == 5 else '',
                'section': '',
            })
            m = maps[-1]
            if m['target'] and m['target'] not in base:
                base[m['target']] = m['start']
        text = await self._command('info target')
        proc = re.search(r'Symbols from "target:(.*)"\.', text).group(1)
        for line in text.strip().split('\n'):
            if ' is .' not in line:
                continue
            if ' in target:' not in line:
                line += ' in target:' + proc
            words = line.split(maxsplit=3)
            start = int(words[0], 16)
            end = int(words[2], 16)
            section, target, = words[3][3:].split(' in target:', maxsplit=1)
            c = 0
            while c < len(maps):
                m = maps[c]
                if not (end <= m['start'] or start >= m['end']):
                    maps.pop(c)
                    c -= 1
                    if start > m['start']:
                        maps.insert(c, {
                            'start': m['start'],
                            'end': start,
                            'offset': 0,
                            'target': m['target'],
                            'section': m['section'],
                        })
                        c += 1
                    if m['end'] > end:
                        maps.insert(c, {
                            'start': end,
                            'end': m['end'],
                            'offset': 0,
                            'target': m['target'],
                            'section': m['section'],
                        })
                        c += 1
                c += 1
            maps.append({
                'start': start,
                'end': end,
                'offset': start - base.get(target, start),
                'target': target,
                'section': section,
            })
        return sorted(filter(lambda i: i['end'] > i['start'], maps), key=lambda i: i['start'])

    async def _info_registers(self):
        registers = {}
        text = await self._command('info registers')
        if re.search(r'The program has no registers now.', text):
            raise GdbError(text.strip())
        for line in text.strip().split('\n'):
            words = line.split()
            registers[words[0]] = int(words[1], 16)
        return registers

    async def _dump(self, start, end):
        temp = tempfile.NamedTemporaryFile()
        try:
            text = await self._command(f'dump binary memory {temp.name} {start} {end}')
            if re.search(r'Cannot access memory at address', text):
                raise GdbError(text.strip())
            temp.seek(0)
            return temp.read()
        finally:
            temp.close()
