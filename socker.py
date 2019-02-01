#!/usr/local/bin/python3
import socket
import threading
from kit import threadid
from decorator import Lock, ilock
from ab import weakmethod, ABMeta


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
        self.queue = list()
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
                self.sender.send(data)  # not none
            self.wait.wait()


class Sender:
    def __init__(self, sock):
        self.sock = sock

    # 发送
    def send(self, data):
        return self.sock.sendall(data)


class Mailbox:
    def __init__(self):
        self.field0 = {
            'send': threading.Event(),
            'recv': dict(),
        }
        self.field1 = {
            'send': threading.Event(),
            'recv': dict(),
        }

    # 订阅
    @ilock()
    def want(self):
        tid = threadid()
        if tid not in self.field1['recv']:
            self.field1['recv'][tid] = threading.Event()
        recv = self.field0['recv'].get(tid)
        if recv is not None:
            recv.set()

    # 完毕
    @ilock()
    def done(self):
        tid = threadid()
        if tid in self.field1['recv']:
            self.field1['recv'].pop(tid)
        recv = self.field0['recv'].get(tid)
        if recv is not None:
            recv.set()

    # 接收
    def recv(self):
        tid = threadid()
        with Lock(self):
            if tid in self.field1['recv']:
                send = self.field1['send']
            elif tid in self.field0['recv']:
                send = self.field0['send']
            else:
                send = None
        assert send is not None
        send.wait()
        return send.data

    # 发送
    def send(self, data):
        with Lock(self):
            self.field0 = self.field1
            self.field1 = {
                'send': threading.Event(),
                'recv': dict(),
            }
            send = self.field0['send']
            send.data = data
            send.set()
            recvs = self.field0['recv'].values()
        for recv in recvs:
            recv.wait()


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
                self.mailbox.send(data)  # not none
            else:
                with Lock(self):
                    self.wait.clear()
                self.wait.wait(timeout=type(self.recver).REST)
        self.mailbox.send(None)  # eof none


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


class MailThread(threading.Thread):
    def __init__(self, mailbox):
        super().__init__()
        self.handlers = list()
        self.wanted = threading.Event()
        self.mailbox = mailbox

    # 数据监听
    @ilock()
    def register(self, handler):
        self.handlers.append(handler)

    def run(self):
        self.mailbox.want()
        self.wanted.set()
        while True:
            data = self.mailbox.recv()
            if data is not None:
                self.mailbox.want()
                with Lock(self):
                    handlers = self.handlers.copy()
                while handlers:
                    handlers.pop(0)(data)
            else:
                self.mailbox.done()
                break


class Socker(metaclass=ABMeta):
    def __init__(self, address, sender=Sender, recver=Recver):
        try:
            self.sock = socket.create_connection(convert_address(address))
            self.send = SendThread(sender(self.sock))
            self.recv = RecvThread(recver(self.sock))
        except BaseException:
            self.is_start = False
            self.is_close = True
            raise
        else:
            self.is_start = False
            self.is_close = False

    # 处理数据（线程）
    def handle(self, data):
        pass

    # 开启线程
    @ilock()
    def start(self):
        if self.is_start or self.is_close:
            return False
        mail = MailThread(self.recv.mailbox)
        mail.register(weakmethod(self, 'handle'))
        mail.start()
        mail.wanted.wait()
        self.send.start()
        self.recv.start()
        self.is_start = True
        return True

    # 关闭连接
    @ilock()
    def close(self):
        if self.is_close:
            return False
        if self.is_start:
            self.recv.close()
            self.send.close()
        self.sock.close()
        self.is_close = True
        return True

    def __aft__(self):
        self.__del__()

    def __del__(self):
        self.close()
