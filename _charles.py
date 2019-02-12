#!/usr/local/bin/python3
import threading
import socket
from decorator import Lock
from socker import create_connection


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
                return None
            except ConnectionResetError:
                data = b''
        else:
            try:
                data = sock.recv(1024)
            except socket.timeout:
                return None
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
            except EOFError:
                self.recver.close()
                break


class ForwardServer:
    def __init__(self, local, remote):
        self.port = local
        self.remote = remote

    # 运行转发服务
    def run(self):
        sock = socket.socket()
        sock.bind(('localhost', self.port,))
        sock.listen(32)
        while True:
            client = SocketWrapper(sock.accept()[0])
            try:
                server = SocketWrapper(create_connection(self.remote))
            except BaseException:
                client.close()
                del client
            else:
                ForwardThread(client, server).start()
                ForwardThread(server, client).start()
                del client, server,
