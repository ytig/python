#!/usr/local/bin/python3
import re
import tempfile
import signal
import asyncio
from asyncio import subprocess


async def gdb_startup(config):
    xs = []
    xs.append('set pagination off')
    xs.append('target remote 127.0.0.1:5039')
    # todo
    args = []
    args.append('--nx')
    args.append('-q')
    for x in xs:
        args.append('-ex')
        args.append(x)
    process = await asyncio.create_subprocess_exec('gdb', *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, limit=2**20)
    await gdb_readlines(process.stdout)
    return process


async def gdb_readlines(stream):
    separator = b'(gdb) '
    return (await stream.readuntil(separator=separator))[:-len(separator)]


class GdbError(RuntimeError):
    pass


class GdbController:
    @classmethod
    async def anew(cls, config):
        self = cls()
        self.process = await gdb_startup(config)
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
            # return (await gdb_readlines(self.process.stdout)).decode()
            print(command)
            text = (await gdb_readlines(self.process.stdout)).decode()
            print(text, end='')
            return text

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

    async def _info_proc_mappings(self):
        maps = []
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
                'offset': int(words[3], 16),
                'objfile': words[-1] if len(words) == 5 else '',
                'section': '.todo',
            })
        return maps

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
