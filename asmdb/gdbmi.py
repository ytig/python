#!/usr/local/bin/python3
import signal
import asyncio
from asyncio import subprocess
from pygdbmi.gdbmiparser import parse_response


async def gdb_startup(config):
    stdin = stdout = subprocess.PIPE
    stderr = subprocess.DEVNULL
    process = await asyncio.create_subprocess_exec('gdb', '--nx', '--interpreter=mi2', '--quiet', stdin=stdin, stdout=stdout, stderr=stderr)
    await gdb_readlines(process.stdout)
    return process


async def gdb_readlines(stream):
    lines = []
    while True:
        line = await stream.readline()
        if not line:
            return lines
        lines.append(parse_response(line.decode()))
        if lines[-1]['type'] == 'done':
            return lines


class GdbError(RuntimeError):
    pass


class GdbDebugger:
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
            for line in await gdb_readlines(self.process.stdout):
                if line['type'] == 'result':
                    if line['message'] == 'done':
                        return line['payload']
                    elif line['message'] == 'error':
                        raise GdbError(line['payload']['msg'])
            raise GdbError('no result')

    async def next(self):
        await self._command('nexti')

    async def step(self):
        await self._command('stepi')

    async def cont(self):
        await self._command('continue')

    async def xb(self, start, end):
        return b'todo xb'
