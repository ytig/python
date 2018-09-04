#!/usr/local/bin/python3
import re
import os
import pexpect
from _pexpect import spawn


def _popen(handle):
    def run(cmd):
        return handle(os.popen(cmd).read())
    return run


def _expect(*expects):
    def run(cmd):
        process = spawn(cmd)
        ret = process.expect(list(expects))
        process.expect(pexpect.EOF)
        process.interact()
        return ret
    return run


class adb:
    # 设备
    @staticmethod
    def devices():
        return _popen(lambda text: [s[:-7] for s in filter(lambda s: s.endswith('\tdevice'), text.split('\n'))])('adb devices')

    # 连接
    @staticmethod
    def connect(addr):
        return _expect('connected to', 'already connected to', 'unable to connect to')('adb connect %s' % (addr,))

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
        return self.execute('root', run=_expect('restarting adbd as root', 'adbd is already running as root'))

    # 限权
    def unroot(self):
        return self.execute('unroot', run=_expect('restarting adbd as non root', 'adbd not running as root'))

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

    # 安装
    def install(self, path):
        return self.execute('install %s' % (path,), run=_expect('Success', 'Failure'))

    # 卸载
    def uninstall(self, package):
        return self.execute('uninstall %s' % (package,), run=_expect('Success', 'Failure'))

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
        return self.am(subcommand, extra, run=_expect('Starting', 'Warning', 'Error'))

    # 服务
    def startservice(self, intent, options='-n', extra={}):
        subcommand = 'startservice %s %s' % (options, intent,)
        return self.am(subcommand, extra, run=_expect('Starting', 'Warning', 'Error'))

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
        return self.am(subcommand, extra, run=_popen(handle))

    # 强退
    def force_stop(self, package):
        return self.execute('shell am force-stop %s' % (package,))
