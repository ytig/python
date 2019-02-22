#!/usr/local/bin/python3
import threading
import socket
from decorator import Lock
from logger import loge, Log


class SocketWrapper:
    def __init__(self, sock):
        self._sock = sock

    # 接收
    def recv(self):
        with Lock(self):
            sock = self._sock
        if sock is None:
            raise EOFError
        if sock.timeout is None:
            try:
                data = sock.recv(1024, socket.MSG_DONTWAIT)
            except BlockingIOError:
                raise TimeoutError
            except ConnectionResetError:
                data = b''
        else:
            try:
                data = sock.recv(1024)
            except socket.timeout:
                raise TimeoutError
            except ConnectionResetError:
                data = b''
        if not data:
            raise EOFError
        return data

    # 发送
    def send(self, data):
        with Lock(self):
            sock = self._sock
        if sock is None:
            raise EOFError
        if data is not None:
            sock.sendall(data)

    # 关闭
    def close(self):
        with Lock(self):
            sock = self._sock
            self._sock = None
        if sock is not None:
            sock.close()


class ForwardThread(threading.Thread):
    def __init__(self, recver, sender):
        super().__init__()
        self.recver = recver
        self.sender = sender

    def run(self):
        while True:
            try:
                self.sender.send(self.recver.recv())
            except TimeoutError:
                pass
            except EOFError:
                self.recver.close()
                break


class ForwardServer:
    def __init__(self, client=SocketWrapper, server=SocketWrapper):
        self.client = client
        self.server = server

    # 运行转发服务
    def run(self, forward, port=8887):
        _host, _port, = forward.split(':')
        _port = int(_port)
        sock = socket.socket()
        sock.bind(('localhost', port,))
        sock.listen(32)
        while True:
            client = self.client(sock.accept()[0])
            try:
                server = self.server(socket.create_connection((_host, _port,)))
            except BaseException:
                client.close()
                del client
                raise
            else:
                ForwardThread(client, server).start()
                ForwardThread(server, client).start()
                del client, server,


class SocketViewer(SocketWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = b''

    def recv(self):
        data = super().recv()
        try:
            self.buffer += data
            while True:
                pack = self._pack()
                if pack is None:
                    break
                self._view(pack)
        except BaseException as e:
            loge(e)
        return data

    def _pack(self):
        if self.buffer:
            buffer = self.buffer
            self.buffer = b''
            return buffer

    def _view(self, pack):
        Log.i(pack)
