#!/usr/local/bin/python3
import re
import json
import copy
import base64
import itertools
import threading
import websocket


class WsError(RuntimeError):
    pass


class Library:
    def __init__(self, ctrl, name, base, size):
        self._ctrl = ctrl
        self._name = name
        self._base = base
        self._size = size

    @property
    def name(self):
        return self._name

    @property
    def base(self):
        return self._base

    @property
    def size(self):
        return self._size


class WsController:
    def __init__(self, url, token, daemon=True):
        self._ws = websocket.create_connection(url, header={
            'cookie': f'token={token}' + (';daemon=true' if daemon else '')
        })
        self._closed = False
        self._struct = {
            'suspend': False,
            'breakpoints': None,
            'watchpoints': None,
            'maps': None
        }
        self._unique = itertools.count(1)
        self._events = {}
        threading.Thread(target=self._run).start()

    @property
    def registers(self):
        """
        Dict of registers.
        """
        return self._pull('reg')

    @property
    def breakpoints(self):
        """
        List of specified breakpoints.
        """
        while self._struct['breakpoints'] is None:
            pass
        return copy.deepcopy(self._struct['breakpoints'])

    @property
    def watchpoints(self):
        """
        List of specified watchpoints.
        """
        while self._struct['watchpoints'] is None:
            pass
        return copy.deepcopy(self._struct['watchpoints'])

    def nexti(self):
        """
        Step one instruction, but proceed through subroutine calls.
        """
        return self._pull('next')

    def stepi(self):
        """
        Step one instruction exactly.
        """
        return self._pull('step')

    def conti(self, timeout=None):
        """
        Continue program being debugged, after signal or breakpoint.
        """
        try:
            return self._pull('cont', timeout=timeout)
        except TimeoutError:
            return False

    def find_library(self, pattern):
        """
        Find a library by name, based on "/proc/$pid/maps" file.
        """
        while self._struct['maps'] is None:
            pass
        name = None
        start = None
        end = None
        for m in self._struct['maps']:
            if name is None:
                if re.search(pattern, m['target']):
                    name = m['target']
                    start = m['start']
                    end = m['end']
            else:
                if name == m['target']:
                    end = m['end']
                else:
                    break
        if name is not None:
            return Library(self, name, start, end - start)
        else:
            return None

    def set_register(self, name, value):
        """
        Assign register by name.
        """
        self._pull('asgn', f'${name}={value}')

    def get_bytes(self, start, length):
        """
        Read memory within a range.
        """
        return base64.b64decode(self._pull('mem', start, start + length))

    def set_bytes(self, start, bytes):
        """
        Write a range of memory.
        """
        for byte in bytes:
            self._pull('asgn', f'*{start}={byte}')
            start += 1

    def set_breakpoint(self, address, disable=False, comment=''):
        """
        Set breakpoint at specified location.
        """
        return self._pull('bpt', [], [{
            'address': address,
            'disable': disable,
            'comment': comment
        }])

    def del_breakpoint(self, address):
        """
        Delete breakpoint at specified location.
        """
        return self._pull('bpt', [{
            'address': address
        }], [])

    def set_watchpoint(self, address):
        """
        Set watchpoint at specified location.
        """
        return self._pull('wpt', [], [{
            'address': address
        }])

    def del_watchpoint(self, address):
        """
        Delete watchpoint at specified location.
        """
        return self._pull('wpt', [{
            'address': address
        }], [])

    def ex(self, command, r=False):
        """
        Execute a single GDB command. (for developing)
        """
        text = self._pull('ex', command)
        if not r:
            print(text.strip())
        else:
            return text

    def _pull(self, method, *params, timeout=None):
        xid = next(self._unique)
        data = {
            'type': 'pull',
            'xid': xid,
            'method': method,
            'params': params
        }
        event = threading.Event()
        self._events[xid] = event
        self._ws.send(json.dumps(data))
        if not event.wait(timeout=timeout):
            raise TimeoutError
        if event.e is not None:
            raise WsError(event.e)
        return event.r

    def _run(self):
        while True:
            try:
                data = self._ws.recv()
            except websocket.WebSocketException:
                data = None
            if not data:
                break
            self._on_message(json.loads(data))
            del data
        self._closed = True

    def _on_message(self, data):
        if data['type'] == 'push':
            if data['key'] == 'exit':
                self._ws.close()
            elif data['key'] in self._struct:
                self._struct[data['key']] = data['val']
        elif data['type'] == 'pull':
            event = self._events.pop(data['xid'], None)
            if event is not None:
                event.r = data['r']
                event.e = data['e']
                event.set()

    def close(self):
        self._ws.close()
        while not self._closed:
            pass
