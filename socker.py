#!/usr/local/bin/python3
import time
import socks
import socket
import threading
from kit import threadid, loge
from decorator import Lock, ilock
from ab import weakmethod
from logger import Log


# 地址转换
def dest_pair(address):
    if isinstance(address, (tuple, list,)):
        return address
    elif isinstance(address, str):
        try:
            host, port, = address.split(':')
            return (host, int(port),)
        except BaseException:
            pass
    raise TypeError


# 代理转换
def socks_map(proxy):
    if proxy is None or isinstance(proxy, dict):
        return proxy
    elif isinstance(proxy, str):
        try:
            type, _proxy, = proxy.split('://')
            if '@' not in _proxy:
                host, port, = _proxy.split(':')
                username = None
                password = None
            else:
                _proxy_l, _proxy_r, = _proxy.split('@')
                host, port, = _proxy_r.split(':')
                username, password, = _proxy_l.split(':')
            return {
                'proxy_type': socks.PROXY_TYPES[type.upper()],
                'proxy_addr': host,
                'proxy_port': int(port),
                'proxy_username': username,
                'proxy_password': password,
            }
        except BaseException:
            pass
    raise TypeError


# 创建连接
def create_connection(address, proxy=None):
    if proxy is None:
        return socket.create_connection(dest_pair(address))
    else:
        return socks.create_connection(dest_pair(address), **socks_map(proxy))


class SendThread(threading.Thread):
    def __init__(self, sender, waker):
        super().__init__()
        self.wait = threading.Event()
        self.closed = None
        self.queue = list()
        self.sender = sender
        self.waker = waker

    # 发送数据
    def send(self, data):
        with Lock(self):
            assert self.closed is None, 'send has been closed'
            self.queue.append(data)
        self.wait.set()

    # 终止发送
    def close(self):
        with Lock(self):
            if self.closed is None:
                self.closed = threading.Event()
        self.wait.set()
        self.closed.wait()

    def run(self):
        closed = False
        while not closed:
            self.wait.wait()
            with Lock(self):
                if self.closed is not None:
                    closed = True
                queue = self.queue.copy()
                self.queue.clear()
                self.wait.clear()
            while queue:
                self._send(queue.pop(0))
        self.closed.set()

    def _send(self, data):
        try:
            self.sender.send(data)
        except BaseException as e:
            Log.e(loge(e))
        else:
            self.waker()


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
    def recv(self, timeout=None):
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
        if not send.wait(timeout=timeout):
            raise TimeoutError
        if send.data is None:
            raise EOFError
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
    def __init__(self, recver, handler, interval):
        super().__init__()
        self.wait = threading.Event()
        self.closer = threading.Event()
        self.closed = threading.Event()
        self.mailbox = Mailbox()
        self.recver = recver
        self.handle_t = HandleThread(handler, weakmethod(self, '_wake'))
        self.interval = interval

    # 接收唤醒
    def wake(self):
        self.wait.set()

    # 终止接收
    def close(self):
        self.closer.set()
        self.wait.set()
        self.closed.wait()
        self.handle_t.closed.wait()

    def start(self):
        self.handle_t.start()
        return super().start()

    def run(self):
        while True:
            if self.closer.wait(timeout=0):
                if self.handle_t.empty():
                    break
            try:
                data = self._recv()
            except EOFError:
                break
            if data is not None:
                self.mailbox.send(data)
                self.handle_t.handle(data)
                del data
            else:
                self.wait.clear()
                self.wait.wait(timeout=self.interval)
        self.mailbox.send(None)
        self.handle_t.handle(None)
        self.closed.set()

    def _wake(self):
        if self.closer.wait(timeout=0):
            self.wait.set()

    def _recv(self):
        try:
            return self.recver.recv()
        except TimeoutError:
            pass
        except EOFError:
            raise
        except BaseException as e:
            Log.e(loge(e))


class HandleThread(threading.Thread):
    def __init__(self, handler, waker):
        super().__init__()
        self.wait = threading.Event()
        self.closed = threading.Event()
        self.queue = list()
        self.handler = handler
        self.waker = waker

    # 处理数据
    def handle(self, data):
        with Lock(self):
            self.queue.append(data)
        self.wait.set()

    # 队列状态
    def empty(self):
        with Lock(self):
            return not self.queue

    def run(self):
        while True:
            self.wait.wait()
            with Lock(self):
                data = self.queue[0]
            self._handle(data)
            del data
            with Lock(self):
                if self.queue.pop(0) is None:
                    break
                if not self.queue:
                    self.wait.clear()
                    self.waker()
        self.closed.set()

    def _handle(self, data):
        try:
            self.handler(data)
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
                    raise TimeoutError
                except ConnectionResetError:
                    data = b''
            else:
                try:
                    data = self.sock.recv(1024)
                except socket.timeout:
                    raise TimeoutError
                except ConnectionResetError:
                    data = b''
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
    def __init__(self, beater, interval):
        super().__init__()
        self.closer = threading.Event()
        self.closed = threading.Event()
        self.beater = beater
        self.interval = interval

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
        try:
            self.beater(repeat)
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
    def start(self, socket_or_address):
        if self._started or self._closed:
            return False
        cls = type(self)
        if isinstance(socket_or_address, socket.socket):
            self.sock = socket_or_address
        else:
            self.sock = create_connection(socket_or_address)
        self.recv_t = RecvThread(cls.RECVER(self.sock), weakmethod(self, 'handle'), cls.RECVER.REST)
        self.send_t = SendThread(cls.SENDER(self.sock), weakmethod(self.recv_t, 'wake'))
        self._beat_t = BeatThread(weakmethod(self, 'beat'), cls.REST)
        self.send_t.start()
        self.recv_t.start()
        self._start()
        self._beat_t.start()
        self._started = True
        return True

    def _start(self):
        pass

    # 发送数据
    def send(self, data, recv=None, timeout=None):
        if recv is None:
            self.send_t.send(data)
        else:
            self.recv_t.mailbox.want()
            try:
                self.send_t.send(data)
                del data
                while True:
                    t = time.time()
                    data = self.recv_t.mailbox.recv(timeout=timeout)
                    dt = time.time() - t
                    if timeout is not None:
                        timeout -= dt
                    if recv(data):
                        return data
                    self.recv_t.mailbox.want()
            finally:
                self.recv_t.mailbox.done()

    def beat(self, repeat):
        self._beat()

    def _beat(self):
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
