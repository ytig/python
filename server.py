#!/usr/local/bin/python3
# coding:utf-8
import time
import inspect
import json
from Crypto.Cipher import AES
from flask import Flask, g, request, make_response, abort
from flask_cors import CORS


# 字符串转整形
def str2int(s, d=None):
    try:
        return int(s)
    except ValueError:
        return d


# 获取请求参数
def param(k, **d):
    kv = request.get_json()
    if kv and k in kv:
        return kv[k]
    kv = request.args
    if kv and k in kv:
        return kv[k]
    return d['d']


class Server(Flask):
    EXPIRE = -1  # 过期时长
    SECRET = None  # 加解密秘钥
    REDIRECT = None  # 重定向响应体

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CORS(self, supports_credentials=True)

    # 加密token
    def encrypt(self, data):
        key = self.SECRET
        if key and data:
            try:
                data = data.encode('utf-8')
                data += b'\xe0'
                data += (-len(data) % 16) * b'\x00'
                data = AES.new(key).encrypt(data)
                data = bytes.hex(data)
            except BaseException:
                data = ''
        return data

    # 解密token
    def decrypt(self, data):
        key = self.SECRET
        if key and data:
            try:
                data = bytes.fromhex(data)
                data = AES.new(key).decrypt(data)
                data = data[:data.rindex(b'\xe0')]
                data = data.decode('utf-8')
            except BaseException:
                data = ''
        return data

    # 读/写token
    def token(self, token=None):
        if token is None:
            token = ''
            join = self.decrypt(str(request.cookies.get('token')))
            index = join.find(',')
            if index != -1:
                expire = str2int(join[:index], d=0)
                if expire < 0 or expire > time.time():
                    token = join[index + 1:]
            if not token and self.REDIRECT:
                abort(make_response(str(self.REDIRECT)))
        else:
            token = str(token)
            join = str(-1 if self.EXPIRE < 0 else int(time.time() + self.EXPIRE)) + ',' + token if token else token
            if not hasattr(g, 'cookies'):
                g.cookies = {}
            g.cookies['token'] = self.encrypt(join)
        return token

    @staticmethod
    def __request(function):
        args = []
        kwargs = {}
        info = inspect.getargspec(function)
        len1 = len(info.args)
        len2 = 0 if not info.defaults else len(info.defaults)
        for i1 in range(len1):
            arg = info.args[i1]
            i2 = i1 + len2 - len1
            if i2 < 0:
                try:
                    args.append(param(arg))
                except KeyError:
                    abort(400)
            else:
                default = info.defaults[i2]
                kwargs[arg] = param(arg, d=default)
        return function(*args, **kwargs)

    @staticmethod
    def __response(ret):
        response = make_response(str(ret))
        if hasattr(g, 'cookies'):
            for k in g.cookies:
                response.set_cookie(k, g.cookies[k])
        return response

    # get请求（装饰器）
    def get(self, rule=None):
        def decorator(function):
            @self.route(rule if rule is not None else '/' + function.__name__.replace('_', '/'), endpoint=function.__name__, methods=['GET'])
            def wrapper():
                return Server.__response(Server.__request(function))
            return wrapper
        return decorator

    # post请求（装饰器）
    def post(self, rule=None):
        def decorator(function):
            @self.route(rule if rule is not None else '/' + function.__name__.replace('_', '/'), endpoint=function.__name__, methods=['POST'])
            def wrapper():
                return Server.__response(Server.__request(function))
            return wrapper
        return decorator


class Json:
    def __str__(self):
        j = {}
        for k in dir(self):
            v = getattr(self, k)
            if not k.startswith('_'):
                j[k] = v
        return json.dumps(j)


class Redirect(Json):
    def __init__(self, redirect):
        self.redirect = redirect


class Success(Json):
    def __init__(self, result, message=''):
        self.state = True
        self.result = result
        self.message = message


class Failure(Json):
    def __init__(self, result, message=''):
        self.state = False
        self.result = result
        self.message = message
