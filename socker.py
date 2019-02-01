#!/usr/local/bin/python3
import socket
import threading
from decorator import Lock, ilock, ithrow
from ab import ABMeta


# 地址格式转换
def convert_address(address):
    if isinstance(address, (list, tuple,)):
        host, port = address
        return (host, int(port),)
    elif isinstance(address, str):
        host, port = address.split(':')
        return (host, int(port),)
    raise TypeError


class SendThread(threading.Thread):
    def __init__(self, sender):
        super().__init__()
        self.queue = []
        self.wait = threading.Event()
        self.shutdown = None
        self.sender = sender

    # 发送数据
    def send(self, data):
        assert data is not None
        with Lock(self):
            assert self.shutdown is None
            self.queue.append(data)
            self.wait.set()

    # 终止发送
    def close(self):
        with Lock(self):
            assert self.shutdown is None
            self.shutdown = threading.Event()
            self.wait.set()
        self.shutdown.wait()

    def run(self):
        while True:
            data = None
            with Lock(self):
                if self.shutdown is not None:
                    self.shutdown.set()
                    break
                if self.queue:
                    data = self.queue.pop(0)
                else:
                    self.wait.clear()
            if data is not None:
                self.sender.send(data)
            self.wait.wait()


class Sender:
    def __init__(self, sock):
        self.sock = sock

    # 发送
    def send(self, data):
        return self.sock.sendall(data)


class Mailbox:
    def want(self):
        pass

    def done(self):
        pass

    def recv(self):
        pass

    def send(self, data):
        pass


class RecvThread(threading.Thread):
    def __init__(self, recver):
        super().__init__()
        self.mailbox = Mailbox()  # 信箱
        self.wait = threading.Event()
        self.shutdown = None
        self.recver = recver

    # 接收唤醒
    def wake(self):
        with Lock(self):
            assert self.shutdown is None
            self.wait.set()

    # 终止接收
    def close(self):
        with Lock(self):
            assert self.shutdown is None
            self.shutdown = threading.Event()
            self.wait.set()
        self.shutdown.wait()

    def run(self):
        while True:
            with Lock(self):
                if self.shutdown is not None:
                    self.shutdown.set()
                    break
            data = self.recver.recv()
            if data is not None:
                self.mailbox.send(data)
            else:
                with Lock(self):
                    self.wait.clear()
                self.wait.wait(timeout=type(self.recver).REST)
        self.mailbox.send(None)


class Recver:
    REST = 3  # 间歇时长

    def __init__(self, sock):
        self.sock = sock
        self.buffer = b''
        self.eof = False

    # 接收
    def recv(self):
        pack = self._pack()
        if pack is None:
            data = self._recv()
            if data:
                self.buffer += data
                pack = self._pack()
        return pack

    def _recv(self):
        buffer = b''
        while not self.eof:
            try:
                data = self.sock.recv(1024, socket.MSG_DONTWAIT)
                if data:
                    buffer += data
                else:
                    self.eof = True
            except BlockingIOError:
                break
        return buffer

    def _pack(self):
        sep = b'\n'
        packs = self.buffer.split(sep, 1)
        if len(packs) == 2:
            self.buffer = packs[1]
            return packs[0] + sep


class Socker(metaclass=ABMeta):
    def __init__(self, address, sender=Sender, recver=Recver):
        self.sock = socket.create_connection(convert_address(address))
        self.send = SendThread(sender(self.sock))
        self.send.start()
        self.recv = RecvThread(recver(self.sock))
        self.recv.start()

    # 关闭连接
    @ilock()
    @ithrow()
    def close(self):
        self.recv.close()
        self.send.close()
        self.sock.close()

    def __del__(self):
        self.close()
