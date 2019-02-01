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
    def __init__(self, sender, waker=None):
        super().__init__()
        self.queue = list()
        self.wait = threading.Event()
        self.shutdown = None
        self.sender = sender
        self.waker = waker

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
                if self.waker is not None:
                    self.waker()
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
        self.eof = False

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
                if not self.eof:
                    send = self.field1['send']
                else:
                    send = self.field0['send']
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
            if data is None:
                self.eof = True
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


class BeatThread(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.handlers = list()
        self.closer = threading.Event()
        self.closed = threading.Event()
        self.interval = interval

    # 心跳监听
    @ilock()
    def register(self, handler):
        self.handlers.append(handler)

    # 终止心跳
    def close(self):
        self.closer.set()
        self.closed.wait()

    def run(self):
        while not self.closer.wait(timeout=self.interval):
            with Lock(self):
                handlers = self.handlers.copy()
            while handlers:
                handlers.pop(0)()
        self.closed.set()


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
                with Lock(self):
                    handlers = self.handlers.copy()
                while handlers:
                    handlers.pop(0)(None)
                break


class Socker(metaclass=ABMeta):
    REST = None  # 心跳间隙

    def __init__(self, address, sender=Sender, recver=Recver):
        try:
            self.sock = socket.create_connection(convert_address(address))
            self.recv_t = RecvThread(recver(self.sock))
            self.send_t = SendThread(sender(self.sock), waker=weakmethod(self.recv_t, 'wake'))
            self._mail_t = MailThread(self.recv_t.mailbox)
            self._mail_t.register(weakmethod(self, 'handle'))
            self._beat_t = BeatThread(type(self).REST)
            self._beat_t.register(weakmethod(self, 'beats'))
        except BaseException:
            self.is_start = False
            self.is_close = True
            raise
        else:
            self.is_start = False
            self.is_close = False

    # 发送数据
    def send(self, data, recv=None):
        if recv is None:
            self.send_t.send(data)
        else:
            self.recv_t.mailbox.want()
            self.send_t.send(data)
            while True:
                data = self.recv_t.mailbox.recv()
                if data is None:
                    self.recv_t.mailbox.done()
                    raise EOFError
                if recv(data):
                    self.recv_t.mailbox.done()
                    return data
                self.recv_t.mailbox.want()

    # 心跳事件（线程触发）
    def beats(self):
        pass

    # 处理数据（线程触发）
    def handle(self, data):
        pass

    # 开启线程
    @ilock()
    def start(self):
        if self.is_start or self.is_close:
            return False
        self._start()
        self.is_start = True
        return True

    # 关闭连接
    @ilock()
    def close(self):
        if self.is_close:
            return False
        if self.is_start:
            self._close()
        self.sock.close()
        self.is_close = True
        return True

    def _start(self):
        self._mail_t.start()
        self._mail_t.wanted.wait()  # 避免漏包
        self.recv_t.start()
        self.send_t.start()
        self._beat_t.start()

    def _close(self):
        self._beat_t.close()
        self.send_t.close()
        self.recv_t.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, t, v, tb):
        self.close()

    def __aft__(self):
        self.__del__()

    def __del__(self):
        self.close()
