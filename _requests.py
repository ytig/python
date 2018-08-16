#!/usr/local/bin/python3
import json
import inspect
import http.cookiejar
import requests.cookies
import requests.sessions
from decorator import Lock, ilock, ithrow


# 序列化
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


# 反序列化
def string2cookies(string, catch=False):
    cookies = requests.cookies.cookiejar_from_dict({})
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


class Client(requests.Session):
    # 动态代理
    def _proxies(self):
        pass

    # 读写缓存
    def _cookies(self, string):
        pass

    @ilock()
    @ithrow()
    def __cookies(self):
        cookies = string2cookies(self._cookies(None))
        if cookies:
            if self.cookies:
                cookies.update(self.cookies)
                self._cookies(cookies2string(cookies))
            self.cookies.update(cookies)

    def request(self, *args, **kwargs):
        self.__cookies()
        method = super().request
        ba = inspect.signature(method).bind(*args, **kwargs)
        if 'proxies' not in ba.arguments:
            proxies = self._proxies()
            if proxies is not None:
                ba.arguments['proxies'] = proxies
        response = method(*ba.args, **ba.kwargs)
        if response.cookies:
            with Lock(self):
                cookies = string2cookies(self._cookies(None))
                cookies.update(response.cookies)
                self._cookies(cookies2string(cookies))
        return response

    def __del__(self):
        self.close()
