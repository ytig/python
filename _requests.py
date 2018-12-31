#!/usr/local/bin/python3
import json
import inspect
import threading
import http.cookiejar
import requests
from decorator import ilock


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
    def disuses(self, plug):
        self._all_plugs.remove(plug)
        return self

    # 使用临时插件
    def use(self, plug):
        self._one_plugs.append(plug)
        return self

    # 停用临时插件
    def disuse(self, plug):
        self._one_plugs.remove(plug)
        return self

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

    # 请求后
    def response(self, session, response):
        pass


# Cookie序列化
def cookies2string(cookies, catch=False):
    string = ''
    if cookies:
        try:
            _cookies = {}
            for domain, paths, in cookies._cookies.items():
                _cookies[domain] = {}
                for path, names, in paths.items():
                    _cookies[domain][path] = {}
                    for name, cookie, in names.items():
                        _cookies[domain][path][name] = {
                            'version': cookie.version,
                            'name': cookie.name,
                            'value': cookie.value,
                            'port': cookie.port,
                            'port_specified': cookie.port_specified,
                            'domain': cookie.domain,
                            'domain_specified': cookie.domain_specified,
                            'domain_initial_dot': cookie.domain_initial_dot,
                            'path': cookie.path,
                            'path_specified': cookie.path_specified,
                            'secure': cookie.secure,
                            'expires': cookie.expires,
                            'discard': cookie.discard,
                            'comment': cookie.comment,
                            'comment_url': cookie.comment_url,
                            'rest': cookie._rest,
                            'rfc2109': cookie.rfc2109,
                        }
            string = json.dumps(_cookies)
        except BaseException:
            string = ''
            if not catch:
                raise
    return string


# Cookie反序列化
def string2cookies(string, catch=False):
    cookies = requests.cookies.cookiejar_from_dict(None)
    if string:
        try:
            _cookies = json.loads(string)
            for domain, paths, in _cookies.items():
                cookies._cookies[domain] = {}
                for path, names, in paths.items():
                    cookies._cookies[domain][path] = {}
                    for name, cookie, in names.items():
                        cookies._cookies[domain][path][name] = http.cookiejar.Cookie(**cookie)
        except BaseException:
            cookies._cookies = {}
            if not catch:
                raise
    return cookies
