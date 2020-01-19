#!/usr/local/bin/python3
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
def params():
    ret = {}
    get = request.args
    if get:
        ret.update(get.to_dict())
    post = request.get_json()
    if post:
        ret.update(post)
    return ret


class Server(Flask):
    EXPIRE = -1  # 过期时长
    SECRET = None  # 加解密秘钥
    REDIRECT = None  # 重定向响应体

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CORS(self, supports_credentials=True)

    # 加密token
    @classmethod
    def encrypt(cls, data):
        key = cls.SECRET
        if key and data:
            try:
                data = data.encode()
                data += b'\xe0'
                data += (-len(data) % 16) * b'\x00'
                data = AES.new(key, AES.MODE_ECB).encrypt(data)
                data = bytes.hex(data)
            except BaseException:
                data = ''
        return data

    # 解密token
    @classmethod
    def decrypt(cls, data):
        key = cls.SECRET
        if key and data:
            try:
                data = bytes.fromhex(data)
                data = AES.new(key, AES.MODE_ECB).decrypt(data)
                data = data[:data.rindex(b'\xe0')]
                data = data.decode()
            except BaseException:
                data = ''
        return data

    # 读/写token
    def token(self, token=None):
        cls = type(self)
        if token is None:
            token = ''
            join = cls.decrypt(str(request.cookies.get('token')))
            index = join.find(',')
            if index != -1:
                expire = str2int(join[:index], d=0)
                if expire < 0 or expire > time.time():
                    token = join[index + 1:]
            if not token and cls.REDIRECT:
                abort(make_response(cls.REDIRECT))
        else:
            token = str(token)
            join = str(-1 if cls.EXPIRE < 0 else int(time.time() + cls.EXPIRE)) + ',' + token if token else token
            if not hasattr(g, 'cookies'):
                g.cookies = {}
            g.cookies['token'] = cls.encrypt(join)
        return token

    # 请求（装饰器）
    def request(self, *methods, rule=None):
        def decorator(function):
            r = rule
            if r is None:
                r = function.__name__.replace('_', '/')
                if not r.startswith('/'):
                    r = '/' + r

            @self.route(r, endpoint=function.__name__, methods=methods)
            def wrapper():
                args = []
                kwargs = {}
                arguments = params()
                argspec = inspect.getargspec(function)
                len1 = len(argspec.args)
                len2 = 0 if not argspec.defaults else len(argspec.defaults)
                for i1 in range(len1):
                    arg = argspec.args[i1]
                    i2 = i1 + len2 - len1
                    if i2 < 0:
                        try:
                            args.append(arguments.pop(arg))
                        except KeyError:
                            abort(400)
                    else:
                        default = argspec.defaults[i2]
                        kwargs[arg] = arguments.pop(arg, default)
                if argspec.keywords is None:
                    arguments.clear()
                ret = make_response(function(*args, **kwargs, **arguments))
                if hasattr(g, 'cookies'):
                    for k in g.cookies:
                        ret.set_cookie(k, g.cookies[k])
                return ret
            return wrapper
        return decorator

    # get请求（装饰器）
    def get(self, rule=None):
        return self.request('GET', rule=rule)

    # post请求（装饰器）
    def post(self, rule=None):
        return self.request('POST', rule=rule)

    # 重定向响应
    def redirect(self, redirect):
        obj = {
            'redirect': redirect,
        }
        return make_response(json.dumps(obj))

    # 成功响应
    def success(self, result, message=''):
        obj = {
            'state': True,
            'result': result,
            'message': message,
        }
        return make_response(json.dumps(obj))

    # 失败响应
    def failure(self, result, message=''):
        obj = {
            'state': False,
            'result': result,
            'message': message,
        }
        return make_response(json.dumps(obj))
