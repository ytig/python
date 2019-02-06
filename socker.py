#!/usr/local/bin/python3
import socket
import threading
from kit import threadid, loge
from decorator import Lock, ilock
from ab import weakmethod
from logger import Log


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
    def __init__(self, sender, waker):
        super().__init__()
        self.queue = list()
        self.wait = threading.Event()
        self.shutdown = None
        self.sender = sender
        self.waker = waker

    # 发送数据
    def send(self, data):
        with Lock(self):
            assert self.shutdown is None, 'send has been closed'
            self.queue.append(data)
        self.wait.set()

    # 终止发送
    def close(self):
        with Lock(self):
            if self.shutdown is None:
                self.shutdown = threading.Event()
        self.wait.set()
        self.shutdown.wait()

    def run(self):
        shutdown = False
        while not shutdown:
            self.wait.wait()
            with Lock(self):
                if self.shutdown is not None:
                    shutdown = True
                queue = self.queue.copy()
                self.queue.clear()
                self.wait.clear()
            while queue:
                self._send(queue.pop(0))
        self.shutdown.set()

    def _send(self, data):
        try:
            self.sender.send(data)
            if self.waker is not None:
                self.waker()
        except BaseException as e:
            Log.e(loge(e))


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
        if tid in self.field0['recv']:
            self.field0['recv'][tid].set()

    # 完毕
    @ilock()
    def done(self):
        tid = threadid()
        if tid in self.field1['recv']:
            self.field1['recv'].pop(tid)
        if tid in self.field0['recv']:
            self.field0['recv'][tid].set()

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
        assert send is not None, 'lack of calling want'
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
    def __init__(self, recver, interval):
        super().__init__()
        self.mailbox = Mailbox()  # 信箱
        self.wait = threading.Event()
        self.shutdown = None
        self.recver = recver
        self.interval = interval

    # 接收唤醒
    def wake(self):
        self.wait.set()

    # 终止接收
    def close(self):
        with Lock(self):
            if self.shutdown is None:
                self.shutdown = threading.Event()
        self.wait.set()
        self.shutdown.wait()

    def run(self):
        while True:
            with Lock(self):
                if self.shutdown is not None:
                    break
            try:
                data = self._recv()
            except EOFError:
                with Lock(self):
                    if self.shutdown is None:
                        self.shutdown = threading.Event()
                    break
            if data is not None:
                self.mailbox.send(data)
            else:
                self.wait.clear()
                self.wait.wait(timeout=self.interval)
        self.mailbox.send(None)
        self.shutdown.set()

    def _recv(self):
        try:
            return self.recver.recv()
        except EOFError:
            raise
        except BaseException as e:
            Log.e(loge(e))


class Recver:
    REST = 3  # 间歇时长

    def __init__(self, sock):
        self.sock = sock
        self.buffer = b''
        self.eof = False

    # 接收
    def recv(self):
        while not self.eof:
            pack = self._pack()
            if pack is not None:
                return pack
            if self.sock.timeout is None:
                try:
                    data = self.sock.recv(1024, socket.MSG_DONTWAIT)
                except BlockingIOError:
                    return None
            else:
                try:
                    data = self.sock.recv(1024)
                except socket.timeout:
                    return None
            if data:
                self.buffer += data
            else:
                self.eof = True
        raise EOFError

    def _pack(self):
        sep = b'\n'
        packs = self.buffer.split(sep, 1)
        if len(packs) == 2:
            self.buffer = packs[1]
            return packs[0] + sep


class BeatThread(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.listeners = list()
        self.closer = threading.Event()
        self.closed = threading.Event()
        self.interval = interval

    # 心跳监听
    @ilock()
    def register(self, listener):
        self.listeners.append(listener)

    # 终止心跳
    def close(self):
        self.closer.set()
        self.closed.wait()

    def run(self):
        self._beat(False)
        while not self.closer.wait(timeout=self.interval):
            self._beat(True)
        self.closed.set()

    def _beat(self, repeat):
        with Lock(self):
            listeners = self.listeners.copy()
        for listener in listeners:
            try:
                listener(repeat)
            except BaseException as e:
                Log.e(loge(e))


class MailThread(threading.Thread):
    def __init__(self, mailbox):
        super().__init__()
        self.listeners = list()
        self.wanted = threading.Event()
        self.closed = threading.Event()
        self.mailbox = mailbox

    # 数据监听
    @ilock()
    def register(self, listener):
        self.listeners.append(listener)

    def run(self):
        self.mailbox.want()
        self.wanted.set()
        while True:
            data = self.mailbox.recv()
            if data is not None:
                self.mailbox.want()
                self._mail(data)
            else:
                self._mail(None)
                self.mailbox.done()
                break
        self.closed.set()

    def _mail(self, data):
        with Lock(self):
            listeners = self.listeners.copy()
        for listener in listeners:
            try:
                listener(data)
            except BaseException as e:
                Log.e(loge(e))


class Socker:
    REST = None  # 心跳间隙
    SENDER = Sender  # 发送者
    RECVER = Recver  # 接收者

    def __init__(self):
        self._started = False
        self._closed = False

    # 开启连接
    @ilock(k='switch')
    def start(self, address):
        if self._started or self._closed:
            return False
        cls = type(self)
        self.sock = socket.create_connection(convert_address(address))
        self.recv_t = RecvThread(cls.RECVER(self.sock), cls.RECVER.REST)
        self._mail_t = MailThread(self.recv_t.mailbox)
        self._mail_t.register(weakmethod(self, 'handle'))
        self.send_t = SendThread(cls.SENDER(self.sock), weakmethod(self.recv_t, 'wake'))
        self._beat_t = BeatThread(cls.REST)
        self._beat_t.register(weakmethod(self, 'beats'))
        self.send_t.start()
        self._mail_t.start()
        self._mail_t.wanted.wait()  # 避免漏包
        self.recv_t.start()
        self._start()
        self._beat_t.start()
        self._started = True
        return True

    def _start(self):
        pass

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

    def beats(self, repeat):
        self._beats()

    def _beats(self):
        pass

    def handle(self, data):
        if data is not None:
            self._handle(data)

    def _handle(self, data):
        pass

    # 关闭连接
    @ilock(k='switch')
    def close(self):
        if self._closed:
            return False
        if self._started:
            self._beat_t.close()
            self._close()
            self.recv_t.close()
            self._mail_t.closed.wait()
            self.send_t.close()
            self.sock.close()
        self._closed = True
        return True

    def _close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.close()
