#!/usr/local/bin/python3
import re
import os
import lxml
import pexpect
from _pexpect import spawn


def popen(handle):
    def run(cmd):
        return handle(os.popen(cmd).read())
    return run


def expect(*expects):
    def run(cmd):
        process = spawn(cmd)
        ret = process.expect(list(expects))
        process.expect(pexpect.EOF)
        process.interact()
        return ret
    return run


class ADB:
    KEYEVENT_HOME = 3  # 桌面
    KEYEVENT_BACK = 4  # 返回
    KEYEVENT_VOLUME_UP = 24  # 升音
    KEYEVENT_VOLUME_DOWN = 25  # 降音
    KEYEVENT_POWER = 26  # 电源
    KEYEVENT_MENU = 82  # 菜单

    # 设备
    @staticmethod
    def devices():
        return popen(lambda text: [s[:-7] for s in filter(lambda s: s.endswith('\tdevice'), text.split('\n'))])('adb devices')

    # 连接
    @staticmethod
    def connect(addr):
        return expect('connected to', 'already connected to', 'unable to connect to')('adb connect %s' % (addr,))

    def __init__(self, serial):
        self.serial = serial

    # 命令
    def execute(self, cmd, run=os.system):
        return run('adb -s %s %s' % (self.serial, cmd,))

    # 重启
    def reboot(self):
        return self.execute('reboot')

    # 权限
    def root(self):
        return self.execute('root', run=expect('restarting adbd as root', 'adbd is already running as root'))

    # 限权
    def unroot(self):
        return self.execute('unroot', run=expect('restarting adbd as non root', 'adbd not running as root'))

    # 上传
    def push(self, local, remote):
        return self.execute('push %s %s' % (local, remote,))

    # 下载
    def pull(self, remote, local):
        return self.execute('pull %s %s' % (remote, local,))

    # 转发
    def forward(self, local, remote=None):
        if remote is None:
            remote = local
        return self.execute('forward %s %s' % (local, remote,))

    # 已装
    def packages(self):
        return self.execute('shell pm list packages', run=popen(lambda text: [s[8:] for s in filter(lambda s: s.startswith('package:'), text.split('\n'))]))

    # 用户
    def uid(self, package):
        return self.execute('shell cat /data/system/packages.list', run=popen(lambda text: ([int(s.split(' ')[1]) for s in filter(lambda s: s.startswith(package), text.split('\n'))] or [None, ])[0]))

    # 安装
    def install(self, path):
        return self.execute('install %s' % (path,), run=expect('Success', 'Failure'))

    # 卸载
    def uninstall(self, package):
        return self.execute('uninstall %s' % (package,), run=expect('Success', 'Failure'))

    # 脚本
    def shell(self, cmd, **kwargs):
        return self.execute('shell %s' % (cmd,), **kwargs)

    # 意图
    def am(self, subcommand, extra, **kwargs):
        cmd = 'shell am %s' % (subcommand,)
        if extra:
            for k, v, in extra.items():
                if isinstance(v, bool):
                    cmd += ' --ez %s %s' % (k, 'true' if v else 'false',)
                elif isinstance(v, int):
                    cmd += ' --ei %s %s' % (k, v,)
                elif isinstance(v, str):
                    cmd += ' --es %s %s' % (k, v,)
        return self.execute(cmd, **kwargs)

    # 界面
    def start(self, intent, options='-n', extra={}):
        subcommand = 'start %s %s' % (options, intent,)
        return self.am(subcommand, extra, run=expect('Starting', 'Warning', 'Error'))

    # 服务
    def startservice(self, intent, options='-n', extra={}):
        subcommand = 'startservice %s %s' % (options, intent,)
        return self.am(subcommand, extra, run=expect('Starting', 'Warning', 'Error'))

    # 广播
    def broadcast(self, intent, options='-a', extra={}):
        subcommand = 'broadcast %s %s' % (options, intent,)

        def handle(text):
            ret = {'code': -1, 'data': '', }
            match = re.search(r'result=(\d+)', text)
            if match is not None:
                ret['code'] = match.group(1)
            match = re.search(r'data="(.*?)"', text)
            if match is not None:
                ret['data'] = match.group(1)
            return ret
        return self.am(subcommand, extra, run=popen(handle))

    # 强退
    def force_stop(self, package):
        return self.execute('shell am force-stop %s' % (package,))

    # 窗口
    def current_focus(self):
        def handle(text):
            start = '  mCurrentFocus='
            for line in text.split('\n'):
                if line.startswith(start):
                    return line.split(' ')[-1][:-1]
            raise EOFError
        return self.execute('shell dumpsys window', run=popen(handle))

    # 视图
    def uiautomator(self, raw=False):
        def handle(text):
            start = 'UI hierchary dumped to: '
            for line in text.split('\n'):
                if line.startswith(start):
                    return line[len(start):]
            raise EOFError
        path = self.execute('shell uiautomator dump', run=popen(handle))
        string = self.execute('shell cat %s' % (path,), run=popen(lambda text: text))
        if raw:
            return string
        else:
            return lxml.etree.fromstring(string.encode('utf-8'))

    # 尺寸
    def size(self):
        def handle(text):
            start = '    init='
            _start = 'cur='
            for line in text.split('\n'):
                if line.startswith(start):
                    for word in line.split(' '):
                        if word.startswith(_start):
                            return [int(i) for i in word[len(_start):].split('x')]
            raise EOFError
        return self.execute('shell dumpsys window displays', run=popen(handle))

    # 点击
    def input_tap(self, x, y):
        return self.execute('shell input tap %s %s' % (x, y,))

    # 滑动
    def input_swipe(self, x1, y1, x2, y2, t):
        return self.execute('shell input swipe %s %s %s %s %s' % (x1, y1, x2, y2, t,))

    # 输入
    def input_text(self, string):
        return self.execute('shell input text %s' % (string,))

    # 按键
    def input_keyevent(self, keycode):
        return self.execute('shell input keyevent %s' % (keycode,))


class Rect:
    # 坐标解析
    @staticmethod
    def from_uiautomator(element):
        bounds = [int(i) for i in element.get('bounds').replace('[', '').replace(']', ',').split(',')[:-1]]
        return Rect(*bounds)

    def __init__(self, left, top, right, bottom):
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)

    # 横轴中心
    @property
    def center_x(self):
        return (self.left + self.right) // 2

    # 纵轴中心
    @property
    def center_y(self):
        return (self.top + self.bottom) // 2

    # 转换字典
    def to_dict(self):
        return {
            'left': self.left,
            'top': self.top,
            'right': self.right,
            'bottom': self.bottom,
        }
