#!/usr/local/bin/python3
import threading
import socket
import logger


class RWLock:
    def __init__(self):
        self.rlock = threading.Lock()
        self.wlock = threading.Lock()
        self.refs = 0

    def acquire_read(self):
        with self.rlock:
            self.refs += 1
            if self.refs == 1:
                self.wlock.acquire()

    def release_read(self):
        with self.rlock:
            self.refs -= 1
            if self.refs == 0:
                self.wlock.release()

    def acquire_write(self):
        self.wlock.acquire()

    def release_write(self):
        self.wlock.release()


class SocketWrapper:
    def __init__(self, sock):
        self.sock = sock
        self.lock = RWLock()

    # 接收
    def recv(self):
        self.lock.acquire_read()
        try:
            if self.sock is None:
                raise EOFError
            if self.sock.timeout is None:
                try:
                    data = self.sock.recv(1024, socket.MSG_DONTWAIT)
                except BlockingIOError:
                    raise TimeoutError
                except ConnectionError:
                    data = b''
            else:
                try:
                    data = self.sock.recv(1024)
                except socket.timeout:
                    raise TimeoutError
                except ConnectionError:
                    data = b''
            if not data:
                raise EOFError
            return data
        finally:
            self.lock.release_read()

    # 发送
    def send(self, data):
        self.lock.acquire_read()
        try:
            if self.sock is None:
                raise EOFError
            if data is not None:
                self.sock.sendall(data)
        finally:
            self.lock.release_read()

    # 关闭
    def close(self):
        self.lock.acquire_write()
        try:
            if self.sock is not None:
                self.sock.close()
                self.sock = None
        finally:
            self.lock.release_write()


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
                self.sender.close()
                break


class ForwardServer:
    def __init__(self, client=SocketWrapper, server=SocketWrapper):
        self.client = client
        self.server = server

    # 运行转发服务
    def run(self, forward, server='localhost:8887'):
        _host, _port, = forward.split(':')
        _port = int(_port)
        host, port = server.split(':')
        port = int(port)
        sock = socket.socket()
        sock.bind((host, port,))
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
            logger.exception(e)
        return data

    def _pack(self):
        if self.buffer:
            buffer = self.buffer
            self.buffer = b''
            return buffer

    def _view(self, pack):
        logger.i(pack)
