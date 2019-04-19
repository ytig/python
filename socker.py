#!/usr/local/bin/python3
import time
import socks
import socket
import inspect
import threading
from kit import weakmethod
from decorator import Lock, ilock
from logger import loge


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
            loge(e)
        else:
            self.waker()


class Sender:
    def __init__(self, sock):
        self.sock = sock

    # 发送
    def send(self, data):
        return self.sock.sendall(data)

    # 中断
    def shutdown(self):
        try:
            self.sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass


class Mailbox:
    def __init__(self):
        self.queue = [threading.Event(), ]
        self.marks = dict()
        self.recv_black_l = list()

    def _gc(self):
        with Lock(self):
            if not self.marks:
                gc = len(self.queue) - 1
            else:
                gc = min(self.marks.values())
            if gc > 0:
                for _ in range(gc):
                    self.queue.pop(0)
                for k in self.marks:
                    self.marks[k] -= gc

    # 发送
    def _send(self, data, *cc):
        cc = list(cc)
        with Lock(self):
            while cc:
                cc.pop(0)(data)
            if data is not None:
                if self.marks:
                    self.queue[-1].data = data
                    self.queue[-1].set()
                    self.queue.append(threading.Event())
            else:
                self.queue[-1].data = None
                self.queue[-1].set()

    # 订阅
    def want(self):
        tid = threading.get_ident()
        with Lock(self):
            assert tid not in self.recv_black_l, 'mailbox already in use'
            if tid not in self.marks:
                self.marks[tid] = len(self.queue) - 1
            else:
                if self.marks[tid] < len(self.queue) - 1:
                    self.marks[tid] += 1
                    self._gc()

    # 完毕
    def done(self):
        tid = threading.get_ident()
        with Lock(self):
            assert tid not in self.recv_black_l, 'mailbox already in use'
            if tid in self.marks:
                self.marks.pop(tid)
                self._gc()

    # 接收
    def recv(self, timeout=None):
        tid = threading.get_ident()
        with Lock(self):
            assert tid not in self.recv_black_l, 'mailbox already in use'
            assert tid in self.marks, 'lack of calling want'
            event = self.queue[self.marks[tid]]
        if not event.wait(timeout=timeout):
            raise TimeoutError
        if event.data is None:
            raise EOFError
        return event.data

    # 封锁
    def __enter__(self):
        tid = threading.get_ident()
        with Lock(self):
            self.recv_black_l.append(tid)

    # 解锁
    def __exit__(self, t, v, tb):
        tid = threading.get_ident()
        with Lock(self):
            self.recv_black_l.remove(tid)


class RecvThread(threading.Thread):
    def __init__(self, recver, handler, interval):
        super().__init__()
        self.blocking = False
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
        with Lock(self):
            if self.blocking:
                if self.handle_t.empty():
                    self.blocking = False
                    self._shutdown()
        self.closer.set()
        self.wait.set()
        self.closed.wait()
        self.handle_t.closed.wait()

    def start(self):
        self.handle_t.start()
        return super().start()

    def run(self):
        while True:
            if self.closer.is_set():
                if self.handle_t.empty():
                    break
            try:
                data = self._recv()
            except EOFError:
                break
            if data is not None:
                self.mailbox._send(data, self.handle_t.handle)
                del data
            else:
                self.wait.clear()
                self.wait.wait(timeout=self.interval)
        self.mailbox._send(None, self.handle_t.handle)
        self.closed.set()

    def _wake(self):
        if self.closer.is_set():
            with Lock(self):
                if self.blocking:
                    if self.handle_t.empty():
                        self.blocking = False
                        self._shutdown()
            self.wait.set()

    def _recv(self):
        with Lock(self):
            self.blocking = True
        try:
            return self.recver.recv()
        except TimeoutError:
            pass
        except EOFError:
            raise
        except BaseException as e:
            loge(e)
        finally:
            with Lock(self):
                if not self.blocking:
                    raise EOFError
                self.blocking = False

    def _shutdown(self):
        try:
            self.recver.shutdown()
        except BaseException as e:
            loge(e)


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
            self.queue.append([data, ])
        self.wait.set()

    # 处理标记
    def mark(self):
        assert threading.current_thread() is not self, 'may lead to deadlock'
        with Lock(self):
            if self.queue:
                mark = threading.Event()
                self.queue[-1].append(mark)
                return mark

    # 队列状态
    def empty(self):
        with Lock(self):
            return not self.queue

    def run(self):
        while True:
            self.wait.wait()
            with Lock(self):
                data = self.queue[0].pop(0)
            eof = data is None
            self._handle(data)
            del data
            with Lock(self):
                for mark in self.queue.pop(0):
                    mark.set()
                mark = None
                if eof:
                    break
                if not self.queue:
                    self.wait.clear()
                    wake = True
                else:
                    wake = False
            if wake:
                self.waker()
        self.closed.set()

    def _handle(self, data):
        try:
            self.handler(data)
        except BaseException as e:
            loge(e)


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

    # 中断
    def shutdown(self):
        try:
            self.sock.shutdown(socket.SHUT_RD)
        except OSError:
            pass


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
            loge(e)


# 一举两得
def stone(function):
    assert inspect.isfunction(function) and not inspect.isgeneratorfunction(function)

    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        finally:
            try:
                self.flush()
            except BaseException:
                pass
    return wrapper


# 流式收发
def stream(generatorfunction):
    assert inspect.isgeneratorfunction(generatorfunction)

    def wrapper(self, *args, **kwargs):
        generator = generatorfunction(self, *args, **kwargs)
        self.recv_t.mailbox.want()
        try:
            with self.recv_t.mailbox:
                recv, timeout, = generator.send(None)
            while True:
                m = time.monotonic()
                try:
                    data = [self.recv_t.mailbox.recv(timeout=timeout), ]
                except TimeoutError as e:
                    with self.recv_t.mailbox:
                        recv, timeout, = generator.throw(type(e), e, e.__traceback__)
                    continue
                except EOFError as e:
                    with self.recv_t.mailbox:
                        generator.throw(type(e), e, e.__traceback__)
                    raise
                dt = time.monotonic() - m
                if timeout is not None:
                    timeout -= dt
                with self.recv_t.mailbox:
                    if recv is None or recv(data[0]):
                        recv, timeout, = generator.send(data.pop())
                data.clear()
                self.recv_t.mailbox.want()
        except StopIteration as e:
            return e.value
        finally:
            self.recv_t.mailbox.done()
    return wrapper


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
                while True:
                    del data
                    m = time.monotonic()
                    data = self.recv_t.mailbox.recv(timeout=timeout)
                    dt = time.monotonic() - m
                    if timeout is not None:
                        timeout -= dt
                    with self.recv_t.mailbox:
                        if recv(data):
                            return data
                    self.recv_t.mailbox.want()
            finally:
                self.recv_t.mailbox.done()

    # 同步数据
    def flush(self):
        mark = self.recv_t.handle_t.mark()
        if mark is not None:
            mark.wait()

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
