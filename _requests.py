#!/usr/local/bin/python3
import json
import inspect
import threading
import http.cookiejar
import requests
from kit import frames
from decorator import Lock, ilock, Throw


class ThreadList:
    def __init__(self):
        self.__lists = dict()

    # 当前列表
    @ilock()
    @property
    def current(self):
        key = threading.current_thread().name
        if key not in self.__lists:
            self.__lists[key] = list()
        return self.__lists[key]

    def __add__(self, *args, **kwargs):
        return self.current.__add__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.current.__contains__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.current.__delitem__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.current.__eq__(*args, **kwargs)

    def __format__(self, *args, **kwargs):
        return self.current.__format__(*args, **kwargs)

    def __ge__(self, *args, **kwargs):
        return self.current.__ge__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.current.__getitem__(*args, **kwargs)

    def __gt__(self, *args, **kwargs):
        return self.current.__gt__(*args, **kwargs)

    def __iadd__(self, *args, **kwargs):
        return self.current.__iadd__(*args, **kwargs)

    def __imul__(self, *args, **kwargs):
        return self.current.__imul__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.current.__iter__(*args, **kwargs)

    def __le__(self, *args, **kwargs):
        return self.current.__le__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self.current.__len__(*args, **kwargs)

    def __lt__(self, *args, **kwargs):
        return self.current.__lt__(*args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return self.current.__mul__(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return self.current.__ne__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self.current.__repr__(*args, **kwargs)

    def __reversed__(self, *args, **kwargs):
        return self.current.__reversed__(*args, **kwargs)

    def __rmul__(self, *args, **kwargs):
        return self.current.__rmul__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.current.__setitem__(*args, **kwargs)

    def __sizeof__(self, *args, **kwargs):
        return self.current.__sizeof__(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        return self.current.__str__(*args, **kwargs)

    def append(self, *args, **kwargs):
        return self.current.append(*args, **kwargs)

    def clear(self, *args, **kwargs):
        return self.current.clear(*args, **kwargs)

    def copy(self, *args, **kwargs):
        return self.current.copy(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self.current.count(*args, **kwargs)

    def extend(self, *args, **kwargs):
        return self.current.extend(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self.current.index(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.current.insert(*args, **kwargs)

    def pop(self, *args, **kwargs):
        return self.current.pop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.current.remove(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        return self.current.reverse(*args, **kwargs)

    def sort(self, *args, **kwargs):
        return self.current.sort(*args, **kwargs)


class Socket(requests.Session):
    def __init__(self):
        super().__init__()
        self._all_plugs = list()
        self._one_plugs = ThreadList()

    # 使用永久插件
    def uses(self, plug):
        self._all_plugs.append(plug)
        return self

    # 停用永久插件
    def disuses(self, plug=None):
        if plug is None:
            self._all_plugs.clear()
        else:
            self._all_plugs.remove(plug)
        return self

    # 使用临时插件
    def use(self, plug):
        self._one_plugs.append(plug)
        return self

    # 停用临时插件
    def disuse(self, plug=None):
        if plug is None:
            self._one_plugs.clear()
        else:
            self._one_plugs.remove(plug)
        return self

    def prepare_request(self, *args, **kwargs):
        ret = super().prepare_request(*args, **kwargs)
        with frames(keep=lambda f: f.f_code is Socket.request.__code__) as f:
            if f.has():
                for plug in f[0].f_locals['plugs']:
                    plug.prepare(self, ret)
        return ret

    def request(self, *args, **kwargs):
        method = super().request
        plugs = list()
        plugs.extend(self._all_plugs)
        plugs.extend(self._one_plugs)
        self._one_plugs.clear()
        ba = inspect.signature(method).bind(*args, **kwargs)
        for plug in plugs:
            plug.request(self, ba.arguments)
        ret = method(*ba.args, **ba.kwargs)
        for plug in reversed(plugs):
            plug.response(self, ret)
        return ret


class Plug:
    # 请求前
    def request(self, session, arguments):
        pass

    # 请求中
    def prepare(self, session, request):
        pass

    # 请求后
    def response(self, session, response):
        pass


class CookiePlug(Plug):
    # Cookie键值化
    @staticmethod
    def cookie2dict(c):
        d = {}
        if c:
            for domain, paths, in c._cookies.items():
                for path, names, in paths.items():
                    for name, cookie, in names.items():
                        d[json.dumps([domain, path, name, ])] = json.dumps([
                            cookie.version,
                            cookie.name,
                            cookie.value,
                            cookie.port,
                            cookie.port_specified,
                            cookie.domain,
                            cookie.domain_specified,
                            cookie.domain_initial_dot,
                            cookie.path,
                            cookie.path_specified,
                            cookie.secure,
                            cookie.expires,
                            cookie.discard,
                            cookie.comment,
                            cookie.comment_url,
                            cookie._rest,
                            cookie.rfc2109,
                        ])
        return d

    # Cookie实例化
    @staticmethod
    def dict2cookie(d):
        c = requests.cookies.cookiejar_from_dict(None)
        if d:
            for key, value, in d.items():
                domain, path, name, = json.loads(key)
                if domain not in c._cookies:
                    c._cookies[domain] = {}
                if path not in c._cookies[domain]:
                    c._cookies[domain][path] = {}
                c._cookies[domain][path][name] = http.cookiejar.Cookie(*json.loads(value))
        return c

    # Cookie读取
    @classmethod
    def load(cls, session):
        cookies = CookiePlug.dict2cookie(session.load_cookie_dict())
        if cookies:
            session.cookies.update(cookies)

    # Cookie保存
    @classmethod
    def save(cls, session, response):
        if response.cookies:
            session.save_cookie_dict(CookiePlug.cookie2dict(response.cookies))

    def request(self, session, arguments):
        with Lock(session):
            with Throw(session) as r:
                if not r:
                    type(self).load(session)

    def response(self, session, response):
        type(self).save(session, response)
