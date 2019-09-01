#!/usr/local/bin/python3
import signal
import asyncio
from asyncio import subprocess


async def gdb_startup(config):
    xs = []
    xs.append('set pagination off')
    args = []
    args.append('--nx')
    args.append('-q')
    for x in xs:
        args.append('-ex')
        args.append(x)
    process = await asyncio.create_subprocess_exec('gdb', *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        return self

    async def adel(self):
        self.process.kill()

    def sigint(self):
        if self.cmdlock.locked():
            self.process.send_signal(signal.SIGINT)

    async def _command(self, command):
        async with self.cmdlock:
            self.process.stdin.write(command.encode() + b'\n')
            return (await gdb_readlines(self.process.stdout)).decode()

    async def next(self):
        await self._command('nexti')

    async def step(self):
        await self._command('stepi')

    async def cont(self):
        await self._command('continue')

    async def xb(self, start, end):
        return b'todo xb'
