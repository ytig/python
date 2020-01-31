#!/usr/local/bin/python3
import sys
import json
import copy
import base64
import itertools
import threading
import websocket
_LOCK = threading.RLock()
_COUNT = itertools.count(1)


def unique():
    with _LOCK:
        return next(_COUNT)


class WsError(RuntimeError):
    pass


class WsController:
    def __init__(self, url, token, daemon=True):
        self.ws = websocket.create_connection(url, header={
            'cookie': f'token={token}' + (';daemon=true' if daemon else '')
        })
        self.closed = False
        self.struct = {
            'suspend': False,
            'breakpoints': [],
            'watchpoints': []
        }
        self.events = {}
        threading.Thread(target=self._run).start()

    @property
    def registers(self):
        return self._pull('reg')

    @property
    def breakpoints(self):
        return copy.deepcopy(self.struct['breakpoints'])

    @property
    def watchpoints(self):
        return copy.deepcopy(self.struct['watchpoints'])

    def nexti(self):
        return self._pull('next')

    def stepi(self):
        return self._pull('step')

    def conti(self, timeout=None):
        try:
            return self._pull('cont', timeout=timeout)
        except TimeoutError:
            return False

    def get_bytes(self, start, length):
        return base64.b64decode(self._pull('mem', start, start + length))

    def set_breakpoint(self, address, disable=False, comment=''):
        return self._pull('bpt', [], [{
            'address': address,
            'disable': disable,
            'comment': comment
        }])

    def del_breakpoint(self, address):
        return self._pull('bpt', [{
            'address': address
        }], [])

    def set_watchpoint(self, address):
        return self._pull('wpt', [], [{
            'address': address
        }])

    def del_watchpoint(self, address):
        return self._pull('wpt', [{
            'address': address
        }], [])

    def _pull(self, method, *params, timeout=None):
        tag = unique()
        data = {
            'type': 'pull',
            'tag': tag,
            'method': method,
            'params': params
        }
        event = threading.Event()
        self.events[tag] = event
        self.ws.send(json.dumps(data))
        if not event.wait(timeout=timeout):
            raise TimeoutError
        if event.e is not None:
            raise WsError(event.e)
        return event.r

    def _run(self):
        while True:
            try:
                data = self.ws.recv()
            except websocket.WebSocketException:
                data = None
            if not data:
                break
            self._on_message(json.loads(data))
            del data
        self.closed = True

    def _on_message(self, data):
        if data['type'] == 'push':
            if data['key'] == 'emit':
                if data['val'] == 0:
                    self.ws.close()
            elif data['key'] in self.struct:
                self.struct[data['key']] = data['val']
        elif data['type'] == 'pull':
            event = self.events.pop(data['tag'], None)
            if event is not None:
                event.r = data['r']
                event.e = data['e']
                event.set()

    def close(self):
        self.ws.close()
        while not self.closed:
            pass


_ctrl = None


def ctrl():
    global _ctrl
    if _ctrl is None:
        _ctrl = WsController('ws://0.0.0.0:8519/ws', sys.argv[1])
    return _ctrl
